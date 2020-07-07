#!/usr/bin/python2.7
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
"""A tool to help generate training data (jsonl) and upload to Google Cloud Storage (GCS).

Synopsis:
  python2 input_helper_v2.py [MLUSE,]SOURCE... GCS_TARGET
  python2 input_helper_v2.py -t GCS_TARGET [MLUSE,]SOURCE...
  python2 input_helper_v2.py -d DICTIONARY_PATH [MLUSE,]SOURCE...

  e.g. python2 input_helper_v2.py ./*.txt gs://bucket/converted
  e.g. python2 input_helper_v2.py gs://bucket/*.txt gs://bucket/converted
  e.g. python2 input_helper_v2.py train,./*.txt test,~/*.txt gs://bucket/converted
  e.g. python2 input_helper_v2.py gs://bucket/*.pdf gs://bucket/converted

Prerequisites:
  1. This tools runs under python2 (>=2.7.9).
     https://www.python.org/downloads
  2. This tools replies on gsutil to copy and upload files.
     https://cloud.google.com/storage/docs/quickstart-gsutil
  3. The caller should have access to all input files and GCS bucket.
  4. If specified, the dictionary csv should be encoded in UTF-8.

Usage:
  1. Convert all txt under dir1 and dir2 and then upload them into gs://bucket.
    python2 input_helper_v2.py dir1/*.txt dir2/*.txt gs://bucket

  2. Convert txt under dir1 (assign to train set) and dir2 (to test set), and
     then upload them into gs://bucket.
    python2 input_helper_v2.py train,dir1/*.txt test,dir2/*.txt gs://bucket

  3. Convert txt under dir1 (assign to train set), auto split a txt content
     into multiple examples if it is too long, annotate them with a dictionary,
     and then upload them into gs://bucket.
    python2 input_helper_v2.py -d dict.csv -s train,dir1/*.txt gs://bucket

  4. Convert PDF files under dir1(local) and gs://dir2, upload the local PDFs
     and converted input into gs://bucket.
    python2 input_helper_v2.py -t gs://bucket dir1/*.pdf gs://dir2/*.pdf

Description:
  -s, --split
      Whether to auto split the content in one input file into multiple examples
      (as multiple json lines in a converted jsonl file).
      Too long example may get rejected in data import.

  -d, --dictionary
      Specify a dictionary in csv to auto annotate the converted jsonl files.
      If specified, the csv should be encoded in UTF-8.
      Each csv line should be in this format: PATTERN,LABEL[,MATCHING_MODE]
      - PATTERN is a string pattern to match in an example content.
      - LABEL is the label applied if the PATTERN is matched.
      - MATCHING_MODE is the strategy the PATTERN applies in matching. 3 modes:
        'e|E': the PATTERN applies to exact match only. (default)
        'i|I': the PATTERN applies to matches ignore cases.
        'r|R': the PATTERN is a regular expression.
        For 'e' and 'i', the matches are enforced on word boundaries. But for
        'r' there is no such restriction.

      Annotations can not have overlaps. So the order of patterns in csv does
      matter.
      The earlier patterns are matched first and overlapping annotations matched
      by later patterns are skipped.

  -v, --verbose
      Whether to print process details to stderr.
"""

from __future__ import absolute_import
from __future__ import print_function

import argparse
import collections
import csv
import glob
import io
import json
import logging
import os
import re
import shutil
import subprocess
import sys
import tempfile

parser = argparse.ArgumentParser()
parser.add_argument(
    'input_file_pattern',
    nargs='+',
    help='The path to input files, e.g. input_*.txt or gs://bucket/input_*.txt.'
)
parser.add_argument(
    '-t',
    '--target_gcs_directory',
    help='The GCS directory to upload the generated jsonl and csv.')
parser.add_argument(
    '-s',
    '--split',
    action='store_true',
    help='Auto split an input file into multiple examples in conversion if '
         'it is larger than the max size limit of an example. By default '
         'an input file is converted into one example as a whole.')
parser.add_argument(
    '-d',
    '--dictionary',
    help='The dictionary in csv to annotation data. Each line contains a '
         '"pattern,label[,mode]"')
parser.add_argument(
    '-v',
    '--verbose',
    action='store_true',
    help='Whether to print process details to stderr.')

# Enable accessing arguments in FLAGS.xxx
FLAGS = argparse.Namespace()

# The generated csv file name.
CSV_FILE_NAME = 'dataset.csv'

# The data limitations
MAX_EXAMPLE_SIZE_IN_BYTES = 4000
MAX_LABEL_LENGTH = 32
MAX_ANNOTATION_TOKENS = 10
# For external files (such as PDF files) the limit is 2M.
MAX_EXTERNAL_FILE_SIZE_IN_BYTES = 2000000

MLUSE_UNSPECIFIED = 'UNSPECIFIED'
MLUSE_TRAIN = 'TRAIN'
MLUSE_VALIDATION = 'VALIDATION'
MLUSE_TEST = 'TEST'
MLUSE = [MLUSE_UNSPECIFIED, MLUSE_TRAIN, MLUSE_VALIDATION, MLUSE_TEST]

# File extensions for external files which should be kept GCS uris in JSONL.
EXTERNAL_FILE_EXTS = ['.pdf']


class ImportFile:
  """Represents one file to be converted to jsonl and uploaded to gcs."""

  def __init__(self, original_filepath, ml_use=MLUSE_UNSPECIFIED,
               local_copy=''):
    # The original input file path (absolute path), can be local (e.g.
    # /data.txt) or on gcs (e.g. gs://bucket/data.txt)
    self.original_filepath = original_filepath

    # The MLUse of this input file
    self.ml_use = ml_use

    # The local copy of the input file if it is originally on gcs. For local
    # files this field is the same as original_filepath.
    # For PDF files, the local copy can be on GCS is the original path is a GCS
    # uri (starting with gs://).
    self.local_copy = local_copy if local_copy else self.original_filepath

    # The converted output jsonl file (in temp directory) to be uploaded to gcs.
    # Some files may skip conversion (e.g. too long), then this field is empty.
    self.local_output_jsonl = ''


# A label pattern representing a dictionary's csv line.
LabelPattern = collections.namedtuple('LabelPattern',
                                      ['pattern', 'label', 'matching_mode'])

# Valid matching mode in LabelPattern
EXACT_MATCH = 'e'
IGNORE_CASE = 'i'
REGEX = 'r'
MATCHING_MODES = [EXACT_MATCH, IGNORE_CASE, REGEX]

# Represents an annotation in the example. The annotation is in range
# [start, end) with the label. The offsets are in unicode code points.
Annotation = collections.namedtuple('Annotation', ['start', 'end', 'label'])


def _IsGcsPattern(file_pattern):
  """Check if a file_pattern is a gcs file pattern."""
  return file_pattern.startswith('gs://')


def _IsExternalFile(file_path):
  """Check if file_path is an external file path."""
  return os.path.splitext(file_path)[1].lower() in EXTERNAL_FILE_EXTS


def _ListGcsFiles(gcs_file_pattern):
  """List all gcs files of a pattern and return a gcs file list."""
  gsutil_ls_cmd = ' '.join([
      'gsutil',
      'ls',
      gcs_file_pattern,
  ])
  # CalledProcessError is thrown if no file is matched
  output = subprocess.check_output(gsutil_ls_cmd, shell=True)
  # Example output:
  # gs://bucket/file1
  # gs://bucket/file2
  # ...
  return output.splitlines()


def _DownloadGcsFile(gcs_file, local_filename):
  """Download a gcs file as a local file."""
  local_dir = os.path.dirname(local_filename)
  if not os.path.exists(local_dir):
    os.makedirs(local_dir)
  assert os.path.isdir(local_dir), ('%s is not a directory' % local_dir)
  gsutil_cp_cmd = ' '.join(['gsutil', 'cp', gcs_file, local_filename])
  # CalledProcessError is thrown if download fails
  subprocess.check_call(gsutil_cp_cmd, shell=True)


def PrepareImportFilesFromFilePattern(input_file_pattern, import_files):
  """Generate ImportFile from a file pattern and update them into import_files.

  Args:
    input_file_pattern: a file pattern on local or gcs. E.g. *.txt,
      gs://bucket/*.txt. Optionally "mluse" can be the prefix. E.g. train,*.txt
    import_files: A map of all ImporFile, original_filepath -> ImportFile

  Returns:
    number of skipped files
  """
  mluse_and_pattern = input_file_pattern.split(',', 1)
  mluse_str, file_pattern = mluse_and_pattern if len(
      mluse_and_pattern) == 2 else (MLUSE_UNSPECIFIED, mluse_and_pattern[0])
  ml_use = mluse_str.upper()
  assert ml_use in MLUSE, ('Unrecognized MLUse %s in file pattern %s' %
                           (mluse_str, input_file_pattern))

  num_of_skipped = 0
  if _IsGcsPattern(file_pattern):
    # For gcs file, we download them to local first
    gcs_files = _ListGcsFiles(file_pattern)
    local_dir = tempfile.mkdtemp()
    prefix = 0
    for gcs_file in gcs_files:
      # For external files in GCS, we just use the uri.
      if _IsExternalFile(gcs_file):
        import_files[gcs_file] = ImportFile(gcs_file, ml_use=ml_use)
        continue
      prefix += 1  # use prefix to keep the extended name (.txt) at last
      local_filename = os.path.join(
          local_dir, '%d_%s' % (prefix, os.path.basename(gcs_file)))
      _DownloadGcsFile(gcs_file, local_filename)
      import_files[local_filename] = ImportFile(
          gcs_file, ml_use=ml_use, local_copy=local_filename)
      logging.info('Prepared %s as %s (%s)', gcs_file, local_filename, ml_use)
  else:
    # Expand '~', vars and follow links to get absolute local file path
    normalized_pattern = os.path.realpath(
        os.path.expandvars(os.path.expanduser(file_pattern)))
    for local_file in glob.glob(normalized_pattern):
      if local_file in import_files:
        logging.info('Skipped duplicate file %s', local_file)
        num_of_skipped += 1
        continue
      if _IsExternalFile(local_file):
        import_files[local_file] = ImportFile(
            os.path.join(FLAGS.target_gcs_directory,
                         os.path.basename(local_file)),
            ml_use=ml_use,
            local_copy=local_file)
        continue
      import_files[local_file] = ImportFile(local_file, ml_use=ml_use)
      logging.info('Prepared %s (%s)', local_file, ml_use)

  return num_of_skipped


def PrepareImportFiles():
  """Create a list of ImportFile to conversion later.

     This process is doing these things:
     - Parse all input file patterns (*.txt) in FLAGS.input_file_pattern
     - download to local for files on gcs
     - dedup files by file path (to prevent uploading the same file twice)
     - generate a list of ImportFile instances for further process

  Returns:
    A list of ImportFile
  """
  # A map of all ImportFile, original_filepath -> ImportFile.
  import_files = {}
  num_of_skipped = 0
  for input_file_pattern in FLAGS.input_file_pattern:
    logging.info('Preparing input pattern: %s', input_file_pattern)
    num_of_skipped += PrepareImportFilesFromFilePattern(input_file_pattern,
                                                        import_files)

  print('Totally %d files to process (skipped %d duplicate files)' %
        (len(import_files), num_of_skipped))
  return import_files.values()


def _ConvertOneExampleWithExternalFile(gcs_uri):
  """Convert an example with external file into a jsonl string."""
  json_obj = {
      'document': {
          'input_config': {
              'gcs_source': {
                  'input_uris': [gcs_uri]
              },
          },
      },
  }
  return json.dumps(json_obj, ensure_ascii=False)


def _ConvertOneExample(example_content):
  """Convert a pure text example into a jsonl string."""
  json_obj = {
      'annotations': [],
      'text_snippet': {
          'content': example_content
      },
  }
  return json.dumps(json_obj, ensure_ascii=False) + '\n'


def ConvertOneFile(import_file, auto_split, full_output_jsonl):
  """Convert one file and write into output_jsonl.

  Args:
    import_file: A ImportFile to convert
    auto_split: True/False, whether to auto split file if it is too large
    full_output_jsonl: The full file path of the output jsonl
  """
  json_lines = []  # all converted json lines
  example_content = ''  # the current content in an example
  blank_lines = 0
  long_lines = 0
  for line in io.open(import_file.local_copy, 'r'):
    line = line.strip()
    if not line:  # skip blank lines
      blank_lines += 1
      continue
    if len(line) > MAX_EXAMPLE_SIZE_IN_BYTES:  # too long a line
      long_lines += 1
      continue

    if (auto_split and example_content and
        # use >= to leave a place for '\n'
        len(example_content) + len(line) >= MAX_EXAMPLE_SIZE_IN_BYTES):
      json_lines.append(_ConvertOneExample(example_content))
      example_content = ''
    example_content = '\n'.join(filter(None, [example_content, line]))

  if example_content:
    json_lines.append(_ConvertOneExample(example_content))

  with io.open(full_output_jsonl, 'w', encoding='utf-8') as output_file:
    output_file.writelines(json_lines)

  extra_info = ''
  if blank_lines or long_lines:
    extra_info = ' (with%s%s skipped)' % (
        ' %d blank lines' % blank_lines if blank_lines else '',
        ' %d long lines' % long_lines if long_lines else '')
  print('Converted %s to %s%s' %
        (import_file.original_filepath, full_output_jsonl, extra_info))


def ConvertFiles(import_files):
  """Take a list of ImportFile and convert them into jsonl locally.

  Args:
    import_files: A list of ImportFile to be converted.

  Returns:
    A list of ImportFile converted to jsonl locally
    (with local_output_jsonl pointing to a temp file).
  """
  temp_dir = tempfile.mkdtemp()
  # A map of filename -> count to avoid filename conflicts.
  filename_root_dict = {}
  for import_file in import_files:
    basename = os.path.basename(import_file.local_copy)
    filename_root, filename_ext = os.path.splitext(basename)
    output_jsonl = filename_root + '.jsonl'
    # Generates a unique output file name if it already exists
    num_occur = 1
    if filename_root in filename_root_dict:
      num_occur = filename_root_dict[filename_root] + 1
      output_jsonl = filename_root + str(num_occur) + '.jsonl'
    filename_root_dict[filename_root] = num_occur

    full_output_jsonl = os.path.join(temp_dir, output_jsonl)
    if filename_ext == '.jsonl':
      # For jsonl, we assume it is already converted and simply copy it.
      shutil.copyfile(import_file.local_copy, full_output_jsonl)
    elif _IsExternalFile(import_file.original_filepath):
      if not _IsGcsPattern(import_file.local_copy):
        filesize = os.path.getsize(import_file.local_copy)
        if filesize > MAX_EXTERNAL_FILE_SIZE_IN_BYTES:
          print('{} is skipped as it exceeds the max size limit for PDF files '
                '({} bytes). Please split the file.\n'
                'This max size limit also applies when using the PDF files in '
                'GCS as inputs.'.format(import_file.local_copy,
                                        MAX_EXTERNAL_FILE_SIZE_IN_BYTES))
          continue
      with io.open(full_output_jsonl, 'w', encoding='utf-8') as output_file:
        output_file.writelines([
            unicode(
                _ConvertOneExampleWithExternalFile(
                    import_file.original_filepath))])
      logging.info('Converted %s (localpath: %s) to %s',
                   import_file.original_filepath, import_file.local_copy,
                   full_output_jsonl)
    else:
      filesize = os.path.getsize(import_file.local_copy)
      if filesize > MAX_EXAMPLE_SIZE_IN_BYTES and not FLAGS.split:
        print(
            '{} is skipped as it exceeds the max size limit ({} bytes). '
            'Please truncate or split it. Or rerun with "-s" to auto split it.'
            .format(import_file.original_filepath, MAX_EXAMPLE_SIZE_IN_BYTES))
        continue
      ConvertOneFile(import_file, FLAGS.split, full_output_jsonl)

    import_file.local_output_jsonl = full_output_jsonl

  return import_files


def _HasOverlap(a1, a2):
  """Check if the 2 annotations overlap."""
  return (a1.start >= a2.start and a1.start < a2.end or
          a1.end > a2.start and a1.end <= a2.end)


def _AnnotationToJson(annotation):
  return {
      'text_extraction': {
          'text_segment': {
              'start_offset': annotation.start,
              'end_offset': annotation.end
          }
      },
      'display_name': annotation.label
  }


def _AnnotateExample(example, label_patterns):
  """Annotate an example by a list of label_patterns.

  Args:
    example: one example as json object (one line in the jsonl file)
    label_patterns: a list of LabelPattern parsed from dictionary

  Returns:
    The annotated example as json object
  """
  example_text = example['text_snippet']['content']
  annotations = [
      Annotation(start=a['text_extraction']['text_segment']['start_offset'],
                 end=a['text_extraction']['text_segment']['end_offset'],
                 label=a['display_name'])
      for a in example['annotations']
  ]

  def _AddAnnotation(annotation):
    for a in annotations:
      if _HasOverlap(annotation, a):
        return False
    annotations.append(annotation)
    return True

  for label_pattern in label_patterns:
    logging.info('Matching pattern "%s"(%s) to label "%s"',
                 label_pattern.pattern, label_pattern.matching_mode,
                 label_pattern.label)
    if label_pattern.matching_mode == EXACT_MATCH:
      # Exact match word on the boundary
      regex = u'\\b(%s)\\b' % re.escape(label_pattern.pattern)
      matcher = re.finditer(regex, example_text, re.UNICODE)
    elif label_pattern.matching_mode == IGNORE_CASE:
      # Ignore case match word on the boundary
      regex = u'\\b(%s)\\b' % re.escape(label_pattern.pattern)
      matcher = re.finditer(regex, example_text, re.UNICODE | re.IGNORECASE)
    elif label_pattern.matching_mode == REGEX:
      # Use regex to match word (not necessarily on word boundary)
      regex = u'(%s)' % label_pattern.pattern
      matcher = re.finditer(regex, example_text, re.UNICODE)

    for match in matcher:
      if match.start() >= match.end():
        logging.warning('  Skipped empty match at %d', match.start())
        continue
      annotation = Annotation(match.start(), match.end(), label_pattern.label)
      is_added = _AddAnnotation(annotation)
      logging.info('  Matched "%s" at %d %s', match.group(1), match.start(),
                   'but skipped' if not is_added else '')
      if is_added:
        # Try validating annotation, but not blocking
        tokens = len(filter(None, re.split(r'\s+', match.group(1))))
        if not tokens or tokens > MAX_ANNOTATION_TOKENS:
          logging.warning(
              '  Annotation "%s" is probably invalid and get '
              'skipped later. The number of tokens should be '
              'in range [1, 10].', match.group(1))

  example['annotations'] = [_AnnotationToJson(a) for a in annotations]
  return example


def _ParseDictionary(file_path):
  """Parse the dictionary from a file.

  Args:
    file_path: The path for a GCS file or a local file.

  Returns:
    A list of LabelPattern in the same order as listed in the file.
  """
  local_file_path = file_path
  # Download file to local if it is a GCS file
  if _IsGcsPattern(file_path):
    _, local_file_path = tempfile.mkstemp()
    _DownloadGcsFile(file_path, local_file_path)

  label_patterns = []
  pattern_and_mode = {}
  with io.open(local_file_path, 'r', encoding='utf-8') as dict_file:
    csv_reader = csv.reader(dict_file)
    for row in csv_reader:
      if len(row) < 2:
        logging.warning('Skipped malformed line%d "%s" in dictionary',
                        csv_reader.line_num, row)
        continue
      pattern = row[0].strip()
      label = row[1].strip()
      mode = row[2].strip().lower() if len(row) > 2 else ''
      mode = mode if mode in MATCHING_MODES else EXACT_MATCH
      if not pattern or not label:
        logging.warning('Skipped malformed line%d "%s" in dictionary',
                        csv_reader.line_num, row)
        continue
      if (pattern, mode) in pattern_and_mode:
        logging.warning(
            'Skipped duplicate pattern in line%d "%s" in dictionary',
            csv_reader.line_num, row)
        continue
      # Validate label
      m = re.match(r'\w+', label)
      if m and len(m.group(0)) > MAX_LABEL_LENGTH:
        logging.warning(
            'Skipped invalid label in line%d "%s" in dictionary. '
            'Valid labels are at most %d characters long, '
            'with characters in [a-zA-Z0-9_].', csv_reader.line_num, row,
            MAX_LABEL_LENGTH)
        continue
      pattern_and_mode[(pattern, mode)] = 1
      label_patterns.append(LabelPattern(pattern, label, mode))

  logging.info('Parsed %d label patterns from %s', len(label_patterns),
               file_path)
  return label_patterns


def AnnotateFiles(import_files):
  """Annotate import files based on a dictionary if it is there.

  Args:
    import_files: A list of ImportFile to be annotated

  Returns:
    A list of ImportFile with the jsonl annotated.
  """
  if not FLAGS.dictionary:
    return import_files
  label_patterns = _ParseDictionary(FLAGS.dictionary)
  if not label_patterns:
    return import_files

  print('Annotating jsonl files with dictionary in', FLAGS.dictionary)
  for import_file in import_files:
    jsonl_local_path = import_file.local_output_jsonl
    if not jsonl_local_path or not os.path.isfile(jsonl_local_path):
      continue

    json_lines = []  # all annotated json lines
    with io.open(jsonl_local_path, 'r', encoding='utf-8') as jsonl_file:
      for line in jsonl_file:
        example = json.loads(line)
        _AnnotateExample(example, label_patterns)
        json_lines.append(json.dumps(example, ensure_ascii=False) + '\n')
    with io.open(jsonl_local_path, 'w', encoding='utf-8') as output_file:
      output_file.writelines(json_lines)
    logging.info('Annotated %s', jsonl_local_path)

  return import_files


def UploadFiles(converted_files, target_gcs_directory):
  """Take a list of ImportFile, generate csv and upload them all to gcs.

  Args:
     converted_files: A list of ImportFile that has been converted to jsonl
       locally.
     target_gcs_directory: The GCS directory to upload to
  """

  converted_files = [
      f for f in converted_files
      if f.local_output_jsonl and os.path.isfile(f.local_output_jsonl)
  ]
  if not converted_files:
    print('No jsonl files to upload')
    return

  # All files including the csv
  files_to_upload = []

  # Create csv file under the same tmp folder with jsonl files.
  csv_file_path = os.path.join(
      os.path.dirname(converted_files[0].local_output_jsonl), CSV_FILE_NAME)
  with open(csv_file_path, 'w') as f:
    for converted_file in converted_files:
      src_path = converted_file.local_output_jsonl
      dst_path = os.path.join(target_gcs_directory, os.path.basename(src_path))

      # Write csv file: ML_USE,gcs_path
      csv_line = (converted_file.ml_use + ',' + dst_path + '\n').encode('utf8')
      f.write(csv_line)

      # Append jsonl file to files_to_upload list, and escaping spaces in paths.
      files_to_upload.append(src_path.replace(' ', '\\ '))

      if (_IsExternalFile(converted_file.original_filepath) and
          not _IsGcsPattern(converted_file.local_copy)):
        files_to_upload.append(converted_file.local_copy)

  # Append csv file to files_to_upload list
  files_to_upload.append(csv_file_path)

  cmd = 'gsutil -m cp {} {}'.format(' '.join(files_to_upload),
                                    target_gcs_directory)

  print('Uploading %d files (including csv and local PDF files) to %s ...' %
        (len(files_to_upload), target_gcs_directory))
  subprocess.check_call(cmd, shell=True)


def ProcessAndCheckArguments():
  """Process commandline arguments and check if they are valid."""
  if not FLAGS.target_gcs_directory:
    if (len(FLAGS.input_file_pattern) > 1 and
        _IsGcsPattern(FLAGS.input_file_pattern[-1])):
      FLAGS.target_gcs_directory = FLAGS.input_file_pattern[-1]
      FLAGS.input_file_pattern = FLAGS.input_file_pattern[:-1]
    else:
      print('Missing target GCS directory')
      parser.print_help()
      sys.exit(1)

  if not _IsGcsPattern(FLAGS.target_gcs_directory):
    print('Target GCS directory %s is invalid' % FLAGS.target_gcs_directory)
    parser.print_help()
    sys.exit(2)


def main():
  print('Got %d inputs to convert and upload to %s' %
        (len(FLAGS.input_file_pattern), FLAGS.target_gcs_directory))
  import_files = PrepareImportFiles()
  converted_files = ConvertFiles(import_files)
  annotated_files = AnnotateFiles(converted_files)
  UploadFiles(annotated_files, FLAGS.target_gcs_directory)


if __name__ == '__main__':
  parser.parse_args(namespace=FLAGS)
  if FLAGS.verbose:
    logging.basicConfig(level=logging.DEBUG, stream=sys.stderr)
  ProcessAndCheckArguments()
  main()
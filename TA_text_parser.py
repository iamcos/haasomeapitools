from match_pairs    import pair_list
import spacy
from spacy.matcher import PhraseMatcher
from spacy.tokens import Span
import pandas as pd

nlp = spacy.load('en_core_web_sm')
matcher = PhraseMatcher(nlp.vocab)

PAIRS = pair_list()
# print(PAIRS.columns)
pairs_list = []
for column in PAIRS.columns:
    column_list = PAIRS[column].to_list()
    for i in column_list:
        pairs_list.append(i)
patterns = list(nlp.pipe([x for x in pairs_list]))
matcher.add('COIN',None,*patterns)
# print(patterns)
text = pd.read_csv('ml_dataset/Bittrex.3000.script.csv')

docs = list(nlp.pipe(text.text))
docs_with_ents = []
for item in text.short_name:
    doc = nlp(item)
    doc.ents = []
    for match_id, start,end in matcher(doc):
        span=Span(doc,start,end,label='COIN')
        doc.ents = list(doc.ents)+ [span]
        span_root_head = span.root.head
        # print(span_root_head.text, "-->", span.text)
        docs_with_ents.append(doc)
        # print(doc)
        # print(doc.ents)
for doc in docs_with_ents:
    # print(doc.ents)
    for ent in doc.ents:
        # print(ent.label_)
        if ent.label_=='COIN':
            print(ent.text,ent.label_)
        else:
            print(False)
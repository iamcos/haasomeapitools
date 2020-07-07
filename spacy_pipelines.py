import spacy
import pandas as pd
from spacy import displacy
nlp = spacy.load("en_core_web_sm")
pipeline = ['tagger','entityRuler', 'parser','ner','tokenizer','dependencyParser', 'entityRecognizer' 'textCategorizer']

data = pd.read_csv('~/Documents/GitHub/haasomeapitools/ml_dataset/Bittrex.300.script.csv')

# docs = list(nlp.pipe(data['text'], disable = ['tagger', 'parser']))

# for doc in docs: 
#     print(((ent.text, ent.label__) for ent in doc.ents))

ddis = []
with nlp.disable_pipes("tagger", "parser"):
    doc = list(x for x in  data['text'])
    ddis.append(doc)
doc = nlp("I will be tagged and parsed")
print((ddis, doc))
# 2. Restore manually
disabled = nlp.disable_pipes("parser")
doc = nlp("I won't have named entities")
disabled.restore()
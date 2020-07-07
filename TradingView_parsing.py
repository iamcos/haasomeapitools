#!/usr/bin/env python
# coding: utf-8

# In[ ]:


### Starting here 
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer,TfidfVectorizer
from sklearn.base import TransformerMixin
from sklearn.pipeline import Pipeline
import string
from spacy.lang.en.stop_words import STOP_WORDS
from spacy.lang.en import English
import spacy


# In[ ]:




# Create our list of punctuation marks
punctuations = string.punctuation

# Create our list of stopwords
# nlp = spacy.load('en')
stop_words = spacy.lang.en.stop_words.STOP_WORDS


# Load English tokenizer, tagger, parser, NER and word vectors
parser = English()
def spacy_tokenizer(sentence):
    # Creating our token object, which is used to create documents with linguistic annotations.
    mytokens = parser(sentence)

    # Lemmatizing each token and converting each token into lowercase
    mytokens = [ word.lemma_.lower().strip() if word.lemma_ != "-PRON-" else word.lower_ for word in mytokens ]

    # Removing stop words
    mytokens = [ word for word in mytokens if word not in stop_words and word not in punctuations ]

    # return preprocessed list of tokens
    return mytokens
bow_vector = CountVectorizer(tokenizer = spacy_tokenizer, ngram_range=(1,1))
tfidf_vector = TfidfVectorizer(tokenizer = spacy_tokenizer)


# In[ ]:


from tradingview_parser import get_ideas, tokenize_ta
from sklearn.model_selection import train_test_split
# df3 = pd.read_csv('ml_dataset/full_edited_1.csv',sep=';')
# df2= get_ideas(pages=300)['data']
df1 = pd.read_csv('/Users/cosmos/Documents/GitHub/haasomeapitools/ml_dataset/Binance.3000.script.csv')
df2 = pd.read_csv('/Users/cosmos/Documents/GitHub/haasomeapitools/ml_dataset/Bittrex.3000.script.csv')

df3 = pd.concat([df1,df2])
# train, test = train_test_split(df2, test_size=0.2, random_state=42)
X_train, X_test, y_train, y_test = train_test_split(df2['text'],df2['move'],test_size=0.2, random_state=42)
print('Move:', y_train.iloc[0])
print('TradingView Idea:', X_train.iloc[0])
print('Training Data Shape:', X_train.shape)
print('Testing Data Shape:', X_test.shape)

# print(train)
# print(test)


# In[ ]:


# getting bittrex and binance database into one
from tradingview_parser import get_ideas, tokenize_ta
from sklearn.model_selection import train_test_split
df1 = pd.read_csv('/Users/cosmos/Documents/GitHub/haasomeapitools/ml_dataset/Binance.3000.script.csv')
df2 = pd.read_csv('/Users/cosmos/Documents/GitHub/haasomeapitools/ml_dataset/Bittrex.3000.script.csv')

df3 = pd.concat([df1,df2])

try:
    df3.drop(['Unnamed: 0'],inplace=True, axis=1)

except:
    pass
datetime_index = pd.to_datetime(df3.time)
df3.set_index(datetime_index, inplace=True)
df3.drop(['time'],inplace=True, axis=1)
df3.to_csv('combined.csv')
print('Move:', y_train.iloc[0])
print('TradingView Idea:', X_train.iloc[0])
print('Training Data Shape:', X_train.shape)
print('Testing Data Shape:', X_test.shape)

print('Main Database len:', len(df3))


# In[ ]:


# df2.to_csv('ml_dataset/binance_300.csv')
import seaborn as sns
import matplotlib.pyplot as plt
fig = plt.figure(figsize=(8,4))
sns.barplot(x = y_train.unique(), y=y_test.value_counts())
plt.show()
import nltk
import ssl

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context


# In[609]:


import spacy
from collections import Counter
from nltk.corpus import stopwords
nltk.download('stopwords')
stopwords = stopwords.words('english')
stopwords.append('–')
stopwords.append('...')
additional_stopwords = ['chart','think''follow','like','subscribe','possible','cardano','issue','hi','see','miners','vip','good','satoshi','look', 'target', 'support', 'long', 'break', 'breakout', 'exit', 'close']
for i in additional_stopwords:
    stopwords.append(i)
nlp = spacy.load('en_core_web_sm')
punctuations = string.punctuation
def cleanup_text(docs, logging=False):
    texts = []
    counter = 1
    for doc in docs:
        if counter % 1000 == 0 and logging:
            print("Processed %d out of %d documents." % (counter, len(docs)))
        counter += 1
        doc = nlp(doc, disable=[ 'ner'])
        tokens = [tok.lemma_.lower().strip() for tok in doc if tok.lemma_ != '-PRON-']
        tokens = [tok for tok in tokens if tok not in stopwords and tok not in punctuations]
        tokens = ' '.join(tokens)
        texts.append(tokens)
    return pd.Series(texts)
  
train, test = train_test_split(df3, test_size=0.2, random_state=42)
short = train['move'] == "Short"
short_text = train[short]['text']
# print(short_text.head())
long =  train['move'] == "Long"
long_text = train[long]['text']
# print(long_text.head())

short_clean = cleanup_text(short_text)
short_clean = ' '.join(short_clean).split()

long_clean = cleanup_text(long_text)
long_clean = ' '.join(long_clean).split()

short_counts = Counter(short_clean)
long_counts = Counter(long_clean)

short_common_words = [word[0] for word in short_counts.most_common(200)]
short_common_counts = [word[1] for word in short_counts.most_common(200)]

long_common_words = [word[0] for word in long_counts.most_common(200)]
long_common_counts = [word[1] for word in long_counts.most_common(200)]


# for w,c in zip(short_common_words,short_common_counts):
#     print(w,c)


# In[610]:


fig = plt.figure(figsize=(18,6))
sns.barplot(x=short_common_words[0:20], y=short_common_counts[0:20])
plt.title('Most Common Words in Short predictions')
plt.show()
fig = plt.figure(figsize=(18,6))
sns.barplot(x=long_common_words[0:20], y=long_common_counts[0:20])
plt.title('Most Common Words Long predictions ')
plt.show()


# In[611]:


short_common_words_d = {}
long_common_words_d = {'long':"",'short':''}


for w,c in zip(short_common_words,short_common_counts):
    short_common_words_d[w] = c
for w,c in zip(long_common_words,long_common_counts):
    long_common_words_d[w] = c



# print(short_common_words_d,long_common_words_d)
print(len(short_common_words_d),len(long_common_words_d))
short_common_words_df = pd.DataFrame({'short':short_common_words_d})
long_common_words_df = pd.DataFrame({'long':long_common_words_d})
words_df = pd.DataFrame((short_common_words_d,long_common_words_d),{'long':long_common_words_d,'short':short_common_words_d}).T
# print(short_common_words_df,long_common_words_df)
# print(short_common_words_df.values,long_common_words_df.values)
print(words_df.columns)
print(words_df.index)
# print(words_df.values)
print([i for i in words_df])
# for row in words_df['short']:
#     print(row)
print(len(words_df))

words_df['word'] = words_df.index
print(words_df)


# In[617]:


common_words_d = {'short':{},'long':{}}
for w1,c1,w2,c2 in zip(short_common_words,short_common_counts,long_common_words,long_common_counts):
    common_words_d['short'][str(w1)] = c1
    common_words_d['long'][str(w2)]= c2
#     common_words_d['short'] = {w1: c1}
#     common_words_d['long'] = {w2:c2}

# print(common_words_d)
wrdf = pd.DataFrame(common_words_d)


try:
    wrdf['word'] = wrdf.index
    wrdf.reset_index(inplace=True,drop=True)
    wrdf.fillna(0,inplace=True)
except:
    pass
# for i in wrdf['word'][wrdf.short!=0]:
#     print(i)
# print(wrdf[['word','short','long']][wrdf.short>0])
p = [i for i in wrdf['word'][wrdf.short>100][wrdf.long>100]]
# print(p)
# print(len(p))
# print(wrdf['word'][wrdf.short>100][wrdf.long>100])
# print(wrdf.long.max())
dfss = []

df_500_2000 = wrdf[['word','short','long']][wrdf['long']>500][wrdf['long']<2000]
df_500_2000_5 = wrdf[['word','short','long']][wrdf['long']>500][wrdf['long']<2000].iloc[0:5]
df_500_2000_up_to_100 = wrdf[['word','short','long']][wrdf['long']>500][wrdf['long']<2000].loc[0:100]

for i in [df_500_2000,df_500_2000_5,df_500_2000_up_to_100]:
    i.name = 
    print(i,i.name)

# In[613]:


from sklearn.feature_extraction.text import CountVectorizer
from sklearn.base import TransformerMixin
from sklearn.pipeline import Pipeline
from sklearn.svm import LinearSVC
from sklearn.feature_extraction.stop_words import ENGLISH_STOP_WORDS
from sklearn.metrics import accuracy_score
from nltk.corpus import stopwords
import string
import re
import spacy
from spacy.lang.en import English
parser = English()
STOPLIST = set(stopwords.words('english') + list(ENGLISH_STOP_WORDS))
SYMBOLS = " ".join(string.punctuation).split(" ") + ["-", "...", "”", "”"]+additional_stopwords
class CleanTextTransformer(TransformerMixin):
   def transform(self, X, **transform_params):
        return [cleanText(text) for text in X]
   def fit(self, X, y=None, **fit_params):
        return self
def get_params(self, deep=True):
        return {}
    
def cleanText(text):
    text = text.strip().replace("\n", " ").replace("\r", " ")
    text = text.lower()
    return text
def tokenizeText(sample):
    tokens = parser(sample)
    lemmas = []
    for tok in tokens:
        lemmas.append(tok.lemma_.lower().strip() if tok.lemma_ != "-PRON-" else tok.lower_)
    tokens = lemmas
    tokens = [tok for tok in tokens if tok not in STOPLIST]
    tokens = [tok for tok in tokens if tok not in SYMBOLS]
    return tokens


# In[602]:


def printNMostInformative(vectorizer, clf, N):
    feature_names = vectorizer.get_feature_names()
    coefs_with_fns = sorted(zip(clf.coef_[0], feature_names))
    topClass1 = coefs_with_fns[:N]
    topClass2 = coefs_with_fns[:-(N + 1):-1]
    print("Class 1 best: ")
    for feat in topClass1:
        print(feat)
    print("Class 2 best: ")
    for feat in topClass2:
        print(feat)
vectorizer = CountVectorizer(tokenizer=tokenizeText, ngram_range=(1,3))
clf = LinearSVC()

pipe = Pipeline([('cleanText', CleanTextTransformer()), ('vectorizer', vectorizer), ('clf', clf)])
# data
train1 = X_train
labelsTrain1 = y_train
test1 = X_test
labelsTest1 = y_test
# train
pipe.fit(train1, labelsTrain1)
# test
preds = pipe.predict(test1)
print("accuracy:", accuracy_score(labelsTest1, preds))
print("Top 10 features used to predict: ")

printNMostInformative(vectorizer, clf, 10)
pipe = Pipeline([('cleanText', CleanTextTransformer()), ('vectorizer', vectorizer)])
transform = pipe.fit_transform(train1, labelsTrain1)
vocab = vectorizer.get_feature_names()
for i in range(len(train1)):
    s = ""
    indexIntoVocab = transform.indices[transform.indptr[i]:transform.indptr[i+1]]
    numOccurences = transform.data[transform.indptr[i]:transform.indptr[i+1]]
    for idx, num in zip(indexIntoVocab, numOccurences):
        s += str((vocab[idx], num))


# In[614]:


from sklearn import metrics
print(metrics.classification_report(labelsTest1, preds, 
                                    target_names=df3['move'].unique()))


# In[615]:


# print(preds)
df_result = pd.DataFrame({'text':X_test,'label':y_test,'prediction':preds}).reindex()
# print(df_result)
correct_results = df_result[['text','label','prediction']][df_result['label']==df_result['prediction']]
wrong_results = df_result[['text','label','prediction']][df_result['label']!=df_result['prediction']]
print('correct',len(correct_results))
print('wrong',len(wrong_results))


# # PART TWO 

# ### GOALS:
# 
# Semantify sentenses from the database, 
# write recognition patterns for use cases.
# Detect pump/bullrun,jump etc, dump/downtrend etc.
# Identify and parse trading signals.
# Make statistic of how often a coin is mentioned, and give it "semantic score".

# In[ ]:


import spacy
import pandas as pd
from spacy import displacy
nlp = spacy.load("en_core_web_sm")

from pyate.term_extraction_pipeline import TermExtractionPipeline

# pipeline = ['tagger', 'parser','ner','tokenizer','dependencyParser', 'entityrecognizer','entityruler', 'textcategorizer']
try:
    nlp.add_pipe(TermExtractionPipeline())
    data = pd.read_csv('~/Documents/GitHub/haasomeapitools/ml_dataset/Bittrex.3000.script.csv')
except ValueError as e:
    print(f'Looks like there\'s {e}, it already exists')
docs = nlp.pipe(data['text'], disable = ['tagger', 'parser'])

# for doc in docs: 
#     print(((doc, doc.text)))


# doc= (x.text for x in  data.text) #creates tuple



# In[ ]:


def render(nlp):
    displacy.render(nlp,style="dep",jupyter=True, page=True)


# In[ ]:


print(next(nlp.pipe(doc)))


# In[ ]:


import spacy
from pyate.term_extraction_pipeline import TermExtractionPipeline


# In[ ]:


print(render(next(nlp.pipe(doc))))


# In[ ]:


print(next(nlp.pipe(strings))._.combo_basic.sort_values(ascending=False).head())


# In[ ]:


strings = data.text.to_string()
words = nlp(strings)._.combo_basic.sort_values(ascending=False).head(1000)


# In[ ]:


words.to_csv('TW_words.csv')


# In[ ]:


words_csv = pd.read_csv('TW_words.csv')
match_tokens = [i for i in words_csv.word[0:30]]# [We, introduce, methods]


# In[ ]:


print(match_tokens)


# In[ ]:


binance3000 = pd.read_csv('ml_dataset/Binance.300.script.csv')


# In[ ]:


binance_doc = nlp.pipe(binance3000.text)


# In[ ]:


print(next(binance_doc._))


# In[ ]:


binance_doc_list = list(binance_doc)


# In[ ]:


binance_db = pd.DataFrame(binance_doc_list)
print(binance_db)


# In[ ]:





# In[ ]:


print(binance_db.index)


# In[ ]:


binance_doc = [nlp.pipe(i) for i in binance3000.text]


# In[ ]:


print(next(binance_doc._.combo_basic.sort_values(ascending=False).head()))


# In[ ]:


pd.set_option('display.max_rows', 10)


# In[ ]:


binance3000.dropna()
binance_string =binance3000.text.to_string()


# In[ ]:


binance_words = nlp(binance_string)._.combo_basic.sort_values(ascending=False).head(1000)


# In[ ]:


binance3000.text.to_csv('binance3000_texts.csv')


# In[ ]:






# %%
from textacy import preprocessing
df3 = preprocessing.normalize_whitespace(preprocessing.remove_punctuation(df3.text))


# %%
import textacy
textacy.text_utils.KWIC(strings, "language", window_width=35)   
# %%


# %%

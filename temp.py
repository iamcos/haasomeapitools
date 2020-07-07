import spacy
from spacy.matcher import Matcher

nlp=spacy.load("en_core_web_sm")
matcher = Matcher(nlp.vocab)

pattern = [
    {"LOWER": "target"}
]

pattern_targets = [
    {'LOWER':"targets"},
    {"IS_PUNCT":True, "OP":"?"},
    {'IS_DIGIT':True,'OP':'?'},
    {'IS_PUNCT':True,'OP':'?'}]


doc = nlp(
    "After making the iOS update you won't notice a radical system-wide "
    "redesign: nothing like the aesthetic upheaval we got with iOS 7. Most of "
    "iOS 11's furniture remains the same as in iOS 10. But you will discover "
    "some tweaks once you delve a little deeper.")
​print(nlp.vocab.strings)
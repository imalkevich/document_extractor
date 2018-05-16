'''
Utilities module.
'''
import re

import nltk

from nltk import word_tokenize, pos_tag
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

nltk.download('stopwords')
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('wordnet')

REPLACE_BY_SPACE_RE = re.compile(r'[/(){}\[\]\|@,;]')
GOOD_SYMBOLS_RE = re.compile(r'[^0-9a-z #+_]')
STOPWORDS = set(stopwords.words('english'))
wnl = WordNetLemmatizer()

def text_prepare(text):
    text = text.lower()
    text = REPLACE_BY_SPACE_RE.sub(' ', text)
    text = GOOD_SYMBOLS_RE.sub('', text)
    text = ' '.join([x for x in text.split() if x and x not in STOPWORDS])
    text = ' '.join([wnl.lemmatize(i,j[0].lower()) if j[0].lower() in ['a','n','v'] else wnl.lemmatize(i) for i,j in pos_tag(word_tokenize(text))])
    return text.strip()
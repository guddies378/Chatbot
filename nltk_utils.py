import nltk
import numpy as np
from nltk.stem.porter import PorterStemmer
from nltk.corpus import stopwords
import string

nltk.download('punkt')
nltk.download('stopwords')

stemmer = PorterStemmer()
stop_words = set(stopwords.words('english'))

def tokenize(sentence):
    # Tokenize the sentence and remove punctuation
    tokens = nltk.word_tokenize(sentence)
    tokens = [word for word in tokens if word not in string.punctuation]
    return tokens

def stem(word):
    # Stem the word and convert to lowercase
    return stemmer.stem(word.lower())

def bag_of_words(tokenized_sentence, words):
    # Remove stop words and stem the tokenized sentence
    sentence_words = [stem(word) for word in tokenized_sentence if word not in stop_words]
    bag = np.zeros(len(words), dtype=np.float32)
    for idx, w in enumerate(words):
        if w in sentence_words:
            bag[idx] = 1.0
    return bag
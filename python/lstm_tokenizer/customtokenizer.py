import re
from collections import defaultdict
import string
from nltk.stem.snowball import SnowballStemmer
import json


class CustomTokenizer:
    def __init__(self):

        self.stemmer = SnowballStemmer(language='english')
        self.dictionary, self.stopwords = None, None

    def load(self, dictionary_path="dictionary.txt", stopwords_path='stopwords.txt'):

        if self.dictionary is not None:
            raise AssertionError("Tokenizer was already trained!")

        with open(dictionary_path) as f:
            self.dictionary = json.load(f)

        with open(stopwords_path) as f:
            self.stopwords = json.load(f)

    def save(self, dictionary_path="dictionary.txt", stopwords_path='stopwords.txt'):

        if self.dictionary is None:
            raise AssertionError("Tokenizer has not been trained or loaded yet!")

        with open(dictionary_path) as f:
            json.dump(self.dictionary, f)

        with open(stopwords_path) as f:
            json.dump(self.stopwords, f)


    def train(self, sentences, stopwords_path='stopwords.txt', min_occurences=70):

        if self.dictionary is not None:
            raise AssertionError("Tokenizer was already trained!")

        self.dictionary["<PAD>"] = 0
        self.dictionary["<UNK>"] = 1

        # prepare list of words that should be omited

        self.stopwords = list(string.punctuation.replace("!", "").replace("?", ""))
        self.stopwords += [word.strip() for word in open(stopwords_path, 'r')]

        counter = defaultdict(int)

        sentences_tokens = [self.prepare(text) for text in sentences]

        for sentence in sentences_tokens:
            for token in sentence:
                counter[token] += 1

        for word in [word for word, count in counter.items() if count >= min_occurences]:
            self.dictionary[word] = len(self.dictionary)

    def prepare(self, text):
        words = re.findall(r"[A-Za-z]+|[^\w\s]", text.lower())
        words = [w for w in words if w not in self.stopwords]
        words = [self.stemmer.stem(word) for word in words]
        return words

    def tokenize(self, text):
        return [self.dictionary[x] if x in self.dictionary.keys() else 1 for x in self.prepare(text)]

    @property
    def vocab_size(self):
        return len(self.dictionary)
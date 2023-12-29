import re
from collections import defaultdict
from nltk.stem.snowball import SnowballStemmer
import json


class CustomTokenizer:
    def __init__(self):

        self.stemmer = SnowballStemmer(language='english')
        self.dictionary, self.excluded_tokens = None, None

    def load(self, dictionary_path="dictionary.txt", excluded_tokens_path='excluded_tokens.txt'):

        with open(dictionary_path) as f:
            self.dictionary = json.load(f)

        with open(excluded_tokens_path) as f:
            self.excluded_tokens = json.load(f)

    def save(self, dictionary_path="dictionary.json", excluded_tokens_path='excluded_tokens.json'):

        if self.dictionary is None:
            raise AssertionError("Tokenizer has not been trained yet!")

        with open(dictionary_path) as f:
            json.dump(self.dictionary, f)

        with open(excluded_tokens_path) as f:
            json.dump(self.excluded_tokens, f)

    def train(self, sentences, excluded_tokens_path='excluded_tokens.json', min_occurences=70):

        if self.dictionary is not None:
            raise AssertionError("Tokenizer was already trained!")

        self.dictionary["<PAD>"] = 0
        self.dictionary["<UNK>"] = 1

        # prepare list of words that should be omited
        with open(excluded_tokens_path) as f:
            self.excluded_tokens = json.load(f)

        counter = defaultdict(int)

        sentences_tokens = [self.prepare(text) for text in sentences]

        for sentence in sentences_tokens:
            for token in sentence:
                counter[token] += 1

        for word in [word for word, count in counter.items() if count >= min_occurences]:
            self.dictionary[word] = len(self.dictionary)

    def prepare(self, text):
        words = re.findall(r"[A-Za-z]+|[^\w\s]", text.lower())
        words = [w for w in words if w not in self.excluded_tokens]
        words = [self.stemmer.stem(word) for word in words]
        return words

    def tokenize(self, text):
        return [self.dictionary[x] if x in self.dictionary.keys() else 1 for x in self.prepare(text)]

    @property
    def vocab_size(self):
        return len(self.dictionary)

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
            raise AssertionError("Tokenizer has already been trained!")

        self.dictionary = {"<PAD>": 0, "<UNK>": 1}

        # load list of words that should be omitted
        with open(excluded_tokens_path) as f:
            self.excluded_tokens = json.load(f)

        counter = defaultdict(int)

        sentences_words = [self.preprocess_sentence(text) for text in sentences]

        for sentence in sentences_words:
            for word in sentence:
                counter[word] += 1

        for word in [word for word, count in counter.items() if count >= min_occurences]:
            self.dictionary[word] = len(self.dictionary)

    def preprocess_sentence(self, sentence):
        """
        Preprocesses the input sentence by splitting, excluding tokens, and performing stemming.

        :param sentence: The input sentence to be preprocessed.
        :return: A list of preprocessed words.
        """
        words = re.findall(r"[A-Za-z]+|[^\w\s]", sentence.lower())       # split lowercased text into words
        words = [w for w in words if w not in self.excluded_tokens]  # remove excluded tokens
        words = [self.stemmer.stem(word) for word in words]          # perform stemming
        return words

    def tokenize(self, text):
        return [self.dictionary[x] if x in self.dictionary.keys() else 1 for x in self.preprocess_sentence(text)]

    @property
    def vocab_size(self):
        return len(self.dictionary)

import re
from collections import defaultdict
import string
from nltk.stem.snowball import SnowballStemmer


class CustomTokenizer:
    def __init__(self, sentences, stopwords_path='stopwords.txt', min_occurences=70):

        self.stemmer = SnowballStemmer(language='english')

        # prepare tokenizing dictionary
        self.dictionary = defaultdict(lambda: len(self.dictionary))
        self.dictionary["<PAD>"], self.dictionary["<UNK>"]

        # prepare list of words that should be omited
        self.excluded_tokens = list(string.punctuation.replace("!", "").replace("?", ""))
        self.excluded_tokens += [word.strip() for word in open(stopwords_path, 'r')]

        counter = defaultdict(int)

        sentences_tokens = [self.prepare(text) for text in sentences]

        for sentence in sentences_tokens:
            for token in sentence:
                counter[token] += 1

        for word in [word for word, count in counter.items() if count >= min_occurences]:
            self.dictionary[word]

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
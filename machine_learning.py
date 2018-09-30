from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.multiclass import OneVsRestClassifier
from sklearn.naive_bayes import MultinomialNB

from utils import tokenizer

class Predictor(object):
    """Broken"""
    def predict(self):
        count = 0
        vocab = dict()
        for desc in self.unique_values():
            tokens = tokenizer(desc)
            for token in tokens:
                if token not in vocab:
                    vocab[token] = count
                    count += 1
        cv = CountVectorizer(ngram_range=(1, 3), vocabulary=vocab)
        train_set = self.get_train_set()
        test_set = self.get_test_set()
        # Train_set should match the categories in tuple placement (see above.)
        X_vectorized = cv.transform(train_set)
        # tf_transformer = TfidfTransformer(use_idf=False).fit(X_vectorized)
        # X_train_tf = tf_transformer.transform(X_vectorized)
        tfidf_transformer = TfidfTransformer()
        X_train_tfidf = tfidf_transformer.fit_transform(X_vectorized)

        smatrix2 = cv.transform(test_set).todense()

        base_clf = MultinomialNB(alpha=1).fit(X_train_tfidf, self.cats)

        clf = OneVsRestClassifier(base_clf).fit(X_vectorized, self.cats)
        Y_pred = clf.predict(smatrix2)
        print Y_pred
    def get_train_set(self):  # Test with generator instead
        train_set = []
        for cat in self.training_set:
            train_set.append(' '.join(self.training_set[cat]))
        return train_set
    @staticmethod
    def get_test_set():  # Test with generator instead
        return [desc for desc in data['Description']]

if __name__ == '__main__':
    y_train = ('New York', 'London')

    train_set = ("new york nyc big apple", "london uk great britain")
    vocab = {'new york': 0, 'nyc': 1, 'big apple': 2, 'london': 3, 'uk': 4, 'great britain': 5}
    count = CountVectorizer(ngram_range=(1, 2), vocabulary=vocab, analyzer='word')
    test_set = ('nice day in nyc', 'london town', 'hello welcome to the big apple. enjoy it here and london too')

    X_vectorized = count.transform(train_set).todense()
    smatrix2 = count.transform(test_set).todense()

    base_clf = MultinomialNB(alpha=1)

    clf = OneVsRestClassifier(base_clf).fit(X_vectorized, y_train)
    Y_pred = clf.predict(smatrix2)
    print Y_pred

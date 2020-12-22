import pickle
import random
import numpy as np
from sklearn.svm import SVC
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import accuracy_score
import MeCab
import argparse

random.seed(42)

parser = argparse.ArgumentParser()
parser.add_argument('--cv', action='store_true')
parser.add_argument('--test', action='store_true')
args = parser.parse_args()

class Classifier:
    def __init__(self, model_path='./models/model.pkl', vectorizer_path='./models/vectorizer.pkl', label_dict_path='./models/label_dict.pkl'):
        self.tokenizer = MeCab.Tagger('-Owakati')
        self.model_path = model_path
        self.vectorizer_path = vectorizer_path
        self.label_dict_path = label_dict_path
    
    def train(self, data):
        texts, labels = list(zip(*data))
        texts = [self.tokenizer.parse(text) for text in texts]
        self.set_vectorizer(texts)
        X = self.vectorizer.transform(texts)
        X = X.toarray()
        self.set_label_dict(labels)
        Y = np.array([self.label2id[label] for label in labels])
        model = SVC(kernel='linear', random_state=None)
        model.fit(X, Y)
        pickle.dump(model, open(self.model_path, 'wb'))
    
    def evaluate(self, data):
        model = pickle.load(open(self.model_path, 'rb'))
        self.set_vectorizer()
        self.set_label_dict()
        texts, y_true = list(zip(*data))
        texts = [self.tokenizer.parse(text) for text in texts]
        X = self.vectorizer.transform(texts)
        X = X.toarray()
        y_pred = model.predict(X)
        y_pred = [self.id2label[label] for label in y_pred]
        return accuracy_score(y_true=y_true, y_pred=y_pred)
    
    def predict(self, texts):
        model = pickle.load(open(self.model_path, 'rb'))
        self.set_vectorizer()
        self.set_label_dict()
        texts = [self.tokenizer.parse(text) for text in texts]
        X = self.vectorizer.transform(texts)
        X = X.toarray()
        y_pred = model.predict(X)
        y_pred = [self.id2label[label] for label in y_pred]
        return y_pred

    def set_vectorizer(self, texts=None):
        if texts is None:
            vectorizer = pickle.load(open(self.vectorizer_path, 'rb'))
        else:
            vectorizer = TfidfVectorizer()
            vectorizer.fit(texts)
            pickle.dump(vectorizer, open(self.vectorizer_path, 'wb'))
        self.vectorizer = vectorizer
    
    def set_label_dict(self, labels=None):
        if labels is None:
            label_dict = pickle.load(open(self.label_dict_path, 'rb'))
        else:
            label_dict = {label: idx for idx, label in enumerate(set(labels))}
            pickle.dump(label_dict, open(self.label_dict_path, 'wb'))
        self.label2id = label_dict
        self.id2label = {v: k for k, v in label_dict.items()}

def cross_validation_dataloader(data, k=5):
    split_size = len(data) // k
    data = [data[split_size * i: split_size * (i+1)] for i in range(k-1)] + [data[split_size * (k-1):]]
    for i in range(k):
        dev_data = data[i]
        train_data = [ele for j in range(k) for ele in data[j] if not i == j]
        yield train_data, dev_data

"""
def data_split():
    data = [line.strip() for line in open('./data/werewolf_recognize_corpus.tsv').readlines()]
    random.shuffle(data)
    train_data = data[100:]
    test_data = data[:100]
    with open('./data/werewolf_recog_train.tsv', 'w') as of:
        of.write('\n'.join(train_data))
    with open('./data/werewolf_recog_test.tsv', 'w') as of:
        of.write('\n'.join(test_data))
"""

if __name__ == "__main__":
    if args.cv:
        data = [line.strip().split('\t') for line in open('./data/werewolf_recognize_corpus.tsv').readlines()]
        random.shuffle(data)
        classifier = Classifier()
        accs = []
        for train_data, dev_data in cross_validation_dataloader(data):
            classifier.train(train_data)
            acc = classifier.evaluate(dev_data)
            accs.append(acc)
        print(f'acc. avg.: {np.mean(accs)}')
    else:
        classifier = Classifier()
        print('Type message to predict')
        print('[INFO] Type "exit" to quit this system.')
        print()
        while 1:
            text = input('>> ')
            if text == 'exit':
                break
            y_pred = classifier.predict([text])[0]
            print(f'== The intent is [{y_pred}]')
            print()
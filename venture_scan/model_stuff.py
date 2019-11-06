import io
from math import log


def cross_entropy(y_pred, y_true):
    """
    Calculate cross-entropy loss
    :param y_pred: (float) prediction
    :param y_true: (float) real answer
    :return: (float) cross-entropy loss
    """
    if y_true == 1:
        return 0 if y_pred == 0.0 else 1 + log(y_pred)
    else:
        return 0 if y_pred == 1.0 else 1 + log(1 - y_pred)


def valid(y_pred, y_true, cutoff=0.5):
    """
    :param y_pred: (float) prediction
    :param y_true: (float) real answer
    :param cutoff: (float) after this value answer began 1.0
    :return: (int)
    """
    if y_pred > cutoff:
        return y_true
    return {1.0: 0.0, 0.0: 1.0}[y_true]


def open_fasttext_model(path, max_words=168000):
    """
    Get trained fasttext model
    :param path: (str) path to trained model
    :return: (dict) dictionary with model
    """
    fin = io.open(path, 'r', encoding='utf-8', newline='\n', errors='ignore')
    n, d = map(int, fin.readline().split())
    data = {}
    i = 0
    for line in fin:
        i += 1
        if max_words != -1 and i > max_words:
            break
        temp_list = line.rstrip().split()
        curr_key = temp_list[0]
        temp_list.pop(0)
        temp_list = [float(el) for el in temp_list]
        data[curr_key] = temp_list

    return data


def word_to_vector(word, ft_model):
    """
    Get vector from fasttext model
    :param word: (str) word
    :param ft_model: (dict) fasttext model
    :return: (list) vector
    """
    return ft_model[word]

# class ClassifierModel:
#
#     def __init__(self, wv_model, path):
#         self.param = {
#             'bootstrap': False,
#             'max_depth': 10,
#             'max_features': 'sqrt',
#             'min_samples_leaf': 2,
#             'min_samples_split': 2,
#             'n_estimators': 400
#         }
#         self.wv_model = wv_model
#         self.model = RandomForestClassifier(**self.param)
#         self.path = path
#
#     def save(self):
#         with open(self.path + '.pck', 'wb') as f:
#             pickle.dump(self.model, f)
#
#     def load(self):
#         try:
#             self.model = pickle.load(open(self.path + '.pck', 'rb'))
#         except FileNotFoundError:
#             self.model = None
#
#     def fit(self, x_train, y_train, score_function=None):
#         self.model.fit(x_train, y_train)
#         if score_function:
#             return self.score(x_train, y_train, score_function)
#
#     def score(self, x_test, y_test, score_function):
#         return score_func(self, x_test, y_test, score_function)
#
#     def predict(self, text):
#         vector = text_vector(text, self.wv_model)
#         return self.model.predict([vector]), self.model.predict_proba([vector])
#
#     def predict_vec(self, vector):
#         return self.model.predict([vector]), self.model.predict_proba([vector])

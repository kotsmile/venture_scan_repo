from venture_scan.model_stuff import cross_entropy, word_to_vector, open_fasttext_model
from venture_scan.data_processing import load_pickle, save_pickle

from math import floor
import numpy as np
from statistics import mean
from keras import layers, models, optimizers, preprocessing, callbacks

PATH_TO_CHECK_TITLE_DATASET = 'files/datasets/check_title_dataset'
PATH_TO_CHECK_TITLE_MODEL = 'files/models/check_title_model.ie'


def get_check_title_dataset():
    """
    Load unordered check_title_dataset
    :return: (list) check_title_dataset
    """
    path_to_check_title_dataset = PATH_TO_CHECK_TITLE_DATASET

    check_title_dataset = []

    with open(path_to_check_title_dataset, 'r') as f:
        for line in f:
            line = line.strip()
            text, ans, tag = line.split('|')
            ans = float(ans)
            check_title_dataset.append([text, ans, tag])

    return check_title_dataset


def text_to_vector(text, ft_model):
    """
    Text vectorization using fasttext model
    :param text: (str)
    :param ft_model: (dict) fasttext model
    :return: (list) vector
    """
    words = []

    text = text.replace('.', '')
    text = text.replace(',', '')
    if len(text) >= 2:
        text = text[0].lower() + text[1:]

    amount_of_large_letters = 0
    amount_of_special_symbols = 0
    amount_of_numbers = 0

    key_words = ['руб', 'евро', 'дол', 'фунт']

    main_key_words = ['вложили', 'вложил', 'вложила', 'вложился', 'вложилась', 'вложились',
                      'привлек', 'привлекли', 'привлекла', 'привлёк', 'привлекала', 'привлекло',
                      'инвестировал', 'инвестировали', 'инвестировала',
                      'вложит', 'вложат', 'вложут',
                      'инвестируют', 'инвестирует', 'инвестировать',
                      'привлечь',
                      'получила', 'получил', 'получило',
                      'инвестиций', 'инвестициях'
                      ]
    optional_vector = [1.0 if word in text else 0.0 for word in main_key_words]
    for kw in key_words:
        if kw in text:
            amount_of_special_symbols += 1

    for symbol in text:
        if symbol in '0123456789':
            amount_of_numbers += 1
        if symbol.isupper():
            amount_of_large_letters += 1
        if symbol in '$€':
            amount_of_special_symbols += 1

    for word in text.split(' '):
        word = word.lower()

        if word in ft_model:
            words.append(np.array(word_to_vector(word, ft_model)))
        else:
            words.append(np.array([0.0] * len(word_to_vector('кот', ft_model))))

    words = np.array(words)
    vector = list(words.mean(axis=0))

    special_vector = [1.0 if amount_of_numbers > 0 else 0.0,
                      1.0 if amount_of_large_letters > 0 else 0.0,
                      1.0 if amount_of_special_symbols > 0 else 0.0]

    return vector, optional_vector + special_vector


def prepare_check_title_dataset(vector_model, percents=None, k=1):
    """
    Prepare check_title_dataset for fitting and scoring model
    :param vector_model: (dict) fasttext model
    :param percents: [(float) percent train from check_title_dataset,
                      (float) proportion of good,
                      (float) proportion of bad]
    :param k: (int) order of cross-validation
    :return: [[(list) x_train, (list) y_train, (list) x_test, (list) y_test, (list) train_texts, (list) test_texts]]
    """

    if not percents:
        percents = [0.9, 0.5, 0.5]

    if k == 1:
        train_percent = percents[0]
        positive_percent = percents[1]
        negative_percent = percents[2]

        positive = []
        negative = []

        dataset = get_check_title_dataset()

        for sample, ans, _ in dataset:
            if ans == 1.0:
                positive.append(sample)
            elif ans == 0.5 or ans == 0.0:
                negative.append(sample)

        positive = list(set(positive))
        negative = list(set(negative))

        positive_train_len = floor(len(positive) * train_percent)
        negative_train_len = floor(positive_train_len / positive_percent * negative_percent)

        positive_train = positive[:positive_train_len]
        negative_train = negative[:negative_train_len]

        positive_test = positive[positive_train_len:]
        negative_test = negative[negative_train_len:]

        x_train, y_train = [], []
        x_test, y_test = [], []

        train_texts = positive_train + negative_train
        test_texts = positive_test + negative_test

        for el in train_texts:
            word_vec, binary_vec = text_to_vector(el, vector_model)
            x_train.append([word_vec, binary_vec])
            y_train.append(1 if el in positive_train else 0)

        for el in test_texts:
            word_vec, binary_vec = text_to_vector(el, vector_model)
            x_test.append([word_vec, binary_vec])
            y_test.append(1 if el in positive_test else 0)

        return [[x_train, y_train, x_test, y_test, train_texts, test_texts]]
    else:
        data = []
        for i in range(k):
            positive_percent = percents[1]
            negative_percent = percents[2]

            positive = []
            negative = []

            dataset = get_check_title_dataset()

            for sample, ans, _ in dataset:
                if ans == 1.0:
                    positive.append(sample)
                elif ans == 0.5 or ans == 0.0:
                    negative.append(sample)

            positive = list(set(positive))
            negative = list(set(negative))

            positive_test_len = floor(len(positive) / k)
            negative_test_len = floor(positive_test_len / positive_percent * negative_percent)

            positive_test_index = positive_test_len * i
            negative_test_index = negative_test_len * i

            positive_test = positive[positive_test_index: positive_test_index + positive_test_len]
            negative_test = negative[negative_test_index: negative_test_index + negative_test_len]

            positive_train = positive[:positive_test_index] + positive[positive_test_index + positive_test_len:]
            negative_train = negative[:negative_test_index] + negative[negative_test_index + negative_test_len:]

            train_texts = positive_train + negative_train
            test_texts = positive_test + negative_test

            x_train, y_train = [], []
            x_test, y_test = [], []

            for el in train_texts:
                word_vec, binary_vec = text_to_vector(el, vector_model)
                x_train.append([word_vec, binary_vec])
                y_train.append(1 if el in positive_train else 0)

            for el in test_texts:
                word_vec, binary_vec = text_to_vector(el, vector_model)
                x_test.append([word_vec, binary_vec])
                y_test.append(1 if el in positive_test else 0)

            data.append([x_train, y_train, x_test, y_test, train_texts, test_texts])
        return data


# TODO docstrings

class Model:
    def __init__(self, title_features_dim, binary_features_dim):
        dense_input_title = layers.Input(shape=(title_features_dim,))
        dense_input_binary = layers.Input(shape=(binary_features_dim,))

        dense_title = layers.Dense(512, activation='relu')(dense_input_title)
        dense_title = layers.Dense(256, activation='relu')(dense_title)

        dense_binary = layers.Dense(512, activation='relu')(dense_input_binary)
        dense_binary = layers.Dense(256, activation='relu')(dense_binary)

        x = layers.concatenate([dense_title, dense_binary])
        x = layers.Dense(128, activation='relu')(x)
        x = layers.Dense(64, activation='relu')(x)
        x = layers.Dense(32, activation='relu')(x)

        main_output = layers.Dense(1, activation='sigmoid')(x)

        self.model = models.Model(inputs=[dense_input_title, dense_input_binary],
                                  outputs=main_output)

        optimizer = optimizers.Adam(lr=0.0001)

        self.model.compile(optimizer=optimizer, loss='binary_crossentropy')

    def fit(self, x_dense_title_train, x_dense_binary_train, y_train,
            val_split=0.25, patience=10, max_epochs=15, batch_size=32):
        x_dense_title_seq = preprocessing.sequence.pad_sequences(x_dense_title_train)
        x_dense_binary_seq = preprocessing.sequence.pad_sequences(x_dense_binary_train)

        self.model.fit([x_dense_title_seq, x_dense_binary_seq],
                       y_train,
                       batch_size=batch_size,
                       epochs=max_epochs,
                       validation_split=val_split,
                       callbacks=[callbacks.EarlyStopping(monitor='val_loss', patience=patience, min_delta=0.0001)],
                       verbose=0
                       )

    def raw_predict(self, x_dense_title, x_dense_binary):
        x_dense_title_seq = preprocessing.sequence.pad_sequences(x_dense_title)
        x_dense_binary_seq = preprocessing.sequence.pad_sequences(x_dense_binary)

        y = self.model.predict([x_dense_title_seq, x_dense_binary_seq])

        return y

    def predict(self, title, vector_model):
        word_vec, binary_vec = text_to_vector(title, vector_model)
        y = self.raw_predict(np.array([word_vec]), np.array([binary_vec]))
        return y[0]

    def score(self, x_dense_title_test, x_dense_binary_test, y_test):
        y = self.raw_predict(x_dense_title_test, x_dense_binary_test)
        losses_cross_entropy = []
        for y_true, y_pred in zip(y_test, y):
            y_pred = y_pred[0]
            loss_cross_entropy = cross_entropy(y_pred, y_true)
            losses_cross_entropy.append(loss_cross_entropy)
        return mean(losses_cross_entropy)


def create_trained_check_title_model(path_to_ft_model):
    wv_model = open_fasttext_model(path_to_ft_model, max_words=10000)

    x_train, y_train, _, _, _, _ = prepare_check_title_dataset(vector_model=wv_model,
                                                               percents=[1.0, 0.5, 0.5])[0]

    size_of_title_input = len(x_train[0][0])
    size_of_binary_input = len(x_train[0][1])

    model = Model(title_features_dim=size_of_title_input,
                  binary_features_dim=size_of_binary_input)

    title_vec_train = np.array([np.array(title_vec) for title_vec, _ in x_train])
    binary_vec_train = np.array([np.array(binary_vec) for _, binary_vec in x_train])
    y_train = np.array(y_train)

    model.fit(x_dense_title_train=title_vec_train,
              x_dense_binary_train=binary_vec_train,
              y_train=y_train)

    save_pickle(model, PATH_TO_CHECK_TITLE_MODEL)


def check(title, vector_model):
    model = load_pickle(PATH_TO_CHECK_TITLE_MODEL)
    return model.predict(title, vector_model)[0] > 0.5

from venture_scan.data_processing import load_pickle, save_pickle
from venture_scan.model_stuff import open_fasttext_model
from venture_scan.web import all_vc

from venture_scan.components.check_title import check, prepare_check_title_dataset, Model

from statistics import mean
import numpy as np
import time


def new_dump(path_to_ft_model):

    wv_model = open_fasttext_model(path_to_ft_model, max_words=168000)

    path = 'files/dump_vc'
    for title, article, date, link in all_vc(start=345):
        row = f'{title}|{article}|{date}|{link}\n'
        row_print = f'{title}|{article.split("[NL]")[0]}...|{date}|{link}'
        print(row_print)
        if check(title, wv_model):
            print('save')
            with open(path, 'a') as f:
                f.write(row)


def test_check_title_part(path_to_ft_model, cross_val=False):
    wv_model = open_fasttext_model(path_to_ft_model, max_words=10000)

    x_train, y_train, x_test, y_test, _, test_texts = prepare_check_title_dataset(vector_model=wv_model)[0]

    size_of_title_input = len(x_train[0][0])
    size_of_binary_input = len(x_train[0][1])

    model = Model(title_features_dim=size_of_title_input,
                  binary_features_dim=size_of_binary_input, )

    title_vec_train = np.array([np.array(title_vec) for title_vec, _ in x_train])
    binary_vec_train = np.array([np.array(binary_vec) for _, binary_vec in x_train])
    y_train = np.array(y_train)

    title_vec_test = np.array([np.array(title_vec) for title_vec, _ in x_test])
    binary_vec_test = np.array([np.array(binary_vec) for _, binary_vec in x_test])
    y_test = np.array(y_test)
    y1 = []
    y2 = []

    model.fit(x_dense_title_train=title_vec_train,
              x_dense_binary_train=binary_vec_train,
              y_train=y_train)

    score_train = model.score(x_dense_title_test=title_vec_train,
                              x_dense_binary_test=binary_vec_train,
                              y_test=y_train)
    y1.append(1 - score_train)

    score_test = model.score(x_dense_title_test=title_vec_test,
                             x_dense_binary_test=binary_vec_test,
                             y_test=y_test)
    y2.append(1 - score_test)

    save_pickle(model.model, f'files/models/double{score_test}.ie')
    print('train:', score_train)
    print('test:', score_test)

    if cross_val:
        print('\ncross-validation')
        data = prepare_check_title_dataset(vector_model=wv_model,
                                           k=20)
        scores = []
        for x_train, y_train, x_test, y_test, _, test_texts in data:
            size_of_title_input = len(x_train[0][0])
            size_of_binary_input = len(x_train[0][1])

            model = Model(title_features_dim=size_of_title_input,
                          binary_features_dim=size_of_binary_input, )

            title_vec_train = np.array([np.array(title_vec) for title_vec, _ in x_train])
            binary_vec_train = np.array([np.array(binary_vec) for _, binary_vec in x_train])
            y_train = np.array(y_train)

            title_vec_test = np.array([np.array(title_vec) for title_vec, _ in x_test])
            binary_vec_test = np.array([np.array(binary_vec) for _, binary_vec in x_test])
            y_test = np.array(y_test)

            model.fit(x_dense_title_train=title_vec_train,
                      x_dense_binary_train=binary_vec_train,
                      y_train=y_train)

            score_train = model.score(x_dense_title_test=title_vec_train,
                                      x_dense_binary_test=binary_vec_train,
                                      y_test=y_train)

            score_test = model.score(x_dense_title_test=title_vec_test,
                                     x_dense_binary_test=binary_vec_test,
                                     y_test=y_test)

            for t, y in zip(test_texts, y_test):
                prediction = model.predict(t, wv_model)
                loss = 1.0 if (y == 1 and prediction >= 0.5) or (y == 0 and prediction < 0.5) else 0.0
                if loss == 0.0:
                    print('mistake:')
                    print(y, t, prediction)

            print('train:', score_train)
            print('test:', score_test)
            scores.append(score_test)

        print('=====')
        print(scores)
        print(mean(scores))

    # def clean(path, new_path):
    #     """
    #     Automatic/manual checking validation of classifier check_title_dataset
    #     :param path: (str) path of source
    #     :param new_path: (str) path of classification check_title_dataset
    #     :return: none
    #     """
    #     good_kw = {'вложили', 'вложил', 'вложила', 'вложился', 'вложилась', 'вложились', 'вложило',
    #                'привлек', 'привлекли', 'привлекла',
    #                'привлёк', 'привлекала', 'привлекло', 'привлёкла',
    #                'инвестировал', 'инвестировали', 'инвестировала',
    #                'привлечь', 'привлечении'
    #                            'получила', 'получил', 'получили', 'получило', 'подтвердил инвестиции', 'инвестиций'
    #
    #                }
    #
    #     bad_kw = {'вложит', 'вложат', 'вложут', 'вложить',
    #               'заработал', 'заработало', 'заработала'
    #                                          'инвестируют', 'инвестирует', 'инвестировать',
    #               'привлёчет', 'привлечёт', 'привлечет',
    #               'IPO', 'ICO', 'создадут', 'создаст', 'создал',
    #               'запустила', 'запустили', 'запустил', 'кредит', 'долг', 'заем',
    #               'пожертвовали', 'пожертвовал', 'пожертвовалa',
    #               'оценил', 'оценили', 'оценила'}
    #
    #     new_dataset = get_dataset(new_path)
    #     dataset = get_dataset(path)
    #
    #     texts = [t for t, _, _ in new_dataset]
    #
    #     for text, ans, tag in dataset:
    #         if text in texts:
    #             continue
    #         if set(text.split()) & good_kw != set():
    #             ans = 1.0
    #             with open(new_path, 'a') as f:
    #                 f.write(f'{text}|{ans}|{tag}\n')
    #         elif set(text.split()) & bad_kw != set():
    #             ans = 0.0
    #             with open(new_path, 'a') as f:
    #                 f.write(f'{text}|{ans}|{tag}\n')
    #         else:
    #             # print(text, end=' ')
    #             # response = input()
    #             # if response != '' and response != 's':
    #             #     ans = {'1': 1.0, '0': 0.0, '5': 0.5}[response]
    #             # elif response == 's':
    #             #     break
    #             with open(new_path, 'a') as f:
    #                 f.write(f'{text}|{ans}|{tag}\n')
    #

    # def demo(path_to_classifier_model, path_to_ft_model, pretrained_model):
    #     """
    #     Classifier model demonstration on two sources
    #     :param path_to_classifier_model: (str) path to classifier model
    #     :param path_to_classification_dataset: (str) path to existed classification check_title_dataset
    #     :param path_to_ft_model: (str) path to fasttext model
    #     :param pretrained_model: (bool) fit model if not pretrained_model
    #     :return: none
    #     """
    #     print('Choose source: \n1) firrma.ru\n2) vc.ru')
    #     ans = input()
    #     func = ['bad input']
    #     if ans == '1':
    #         func = firmma_by_title
    #     elif ans == '2':
    #         func = vc_by_title
    #
    #     wv_model = open_fasttext_model(path_to_ft_model, max_words=10000)
    #
    #     # model = ClassifierModel(path=path_to_classifier_model, wv_model=wv_model)
    #     # if pretrained_model:
    #     #     model.load()
    #     # else:
    #     #     create_best_class_model(path_to_classification_dataset=path_to_classification_dataset,
    #     #                             path_to_ft_model=path_to_ft_model,
    #     #                             path_to_classifier_model=path_to_classifier_model,
    #     #                             print_=False)
    #
    #     # model.load()
    #     model = load_pickle(path_to_classifier_model)
    #     in_model = model.model
    #     model = Model(title_features_dim=300,
    #                   binary_features_dim=30)
    #     model.model = in_model
    # for title in func():
    #     y = model.predict(title, wv_model)
    #     pred = 1 if y >= 0.5 else 0
    #     print(f'{"+" if pred == 1 else " "}  {y.tolist()[0]:.5f} {title}')

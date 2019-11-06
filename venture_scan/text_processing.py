import re

LONG = '===================='


# target, price, percent, investors, sphere, country

def convert(list_, sep='.'):
    l = []
    for i in range(len(list_)):
        try:
            if list_[i] not in ['-', '<', '>']:
                l.append(list_[i])
            elif list_[i] + list_[i + 1] == '->':
                l.append('->')
            elif list_[i] + list_[i + 1] == '<-':
                l.append('<-')
            elif list_[i] + list_[i + 1] == '-<':
                l.append('<-')
        except IndexError:
            pass
    new_l = l[:]
    l = []
    prev = ''
    for i in new_l:
        if prev != i:
            l.append(i)
        prev = i

    ls = []
    a = []
    for i in l:
        if i != sep:
            a.append(i)
        else:
            ls.append(a[:])
            a = []
    ls.append(a[:])
    new_ls = []
    for sent in ls:
        temp = []
        for w in sent:
            if not (w == '>' or w == '<' or w == '-'):
                temp.append(w)
        new_ls.append(temp)

    return new_ls


def clear(list_):
    result = []
    for items in list_:
        best = ''
        for item in items:
            if len(item) > len(best):
                best = item

        for s in ['инв', 'влож', 'вкла', 'прив']:
            if best.lower().startswith(s):
                best = '-'

        if best == 'в':
            best = '>'
        if best == 'от':
            best = '<'
        result.append(best)
    try:
        new_result = [result[0]]
    except IndexError:
        return 'NaN'
    for i in range(1, len(result)):
        if result[i - 1] != result[i]:
            new_result.append(result[i])
    # print(new_result)
    return new_result


def extract(title, article, info=False, regex=True):
    if regex:
        article = title + '\n ' + article
        article = article.replace('\n', '=')

        response = True
        # привлек. от фонда. венчурн
        money_pattern = r'((\$|\€)\s?\d+\,?\d*\s?(M|М|млрд|млн|мил|тыс)?)|((\d+\,?\d*\s?(млрд|млн|мил|тыс)?\s(руб|евро|дол)))'

        names_pattern = r'(=)|(["«„][А-Я0-9][А-Яа-я0-9&]+["»“])|' \
                        r'([A-Z0-9][A-Za-z&\.]+(\s[A-Z][A-Za-z&\.+]*)*)|\s(в|от)\s|([Ии]нвест|[Вв]лож|[Вв]кла|[Пп]рив)'

        res_money = re.findall(money_pattern, article)
        res_names = re.findall(names_pattern, article)

        # print('money:', clear(res_money))

        cL_res_names1 = clear(res_names)

        res_names1 = convert(cL_res_names1, sep='=')

        target = 'NaN'
        investors = 'NaN'

        tar_more = True
        inv_more = True

        main_found = False

        sw = ['NaN', '->', '<-']

        for sent in res_names1:
            for i in range(len(sent)):
                if sent[i] == '->':
                    try:
                        if sent[i + 1] not in sw and tar_more and not main_found:
                            tar_more = False
                            target = sent[i + 1]
                    except IndexError:
                        pass
                    try:
                        if sent[i - 1] not in sw and inv_more and not main_found:
                            inv_more = False
                            investors = sent[i - 1]
                    except IndexError:
                        pass
                    try:
                        if sent[i - 1] not in sw and sent[i + 1] not in sw and not main_found:
                            main_found = True
                            investors = sent[i - 1]
                            target = sent[i + 1]
                    except IndexError:
                        pass

                elif sent[i] == '<-':
                    try:
                        if sent[i - 1] not in sw and tar_more and not main_found:
                            tar_more = False
                            target = sent[i - 1]
                    except IndexError:
                        pass
                    try:
                        if sent[i + 1] not in sw and inv_more and not main_found:
                            inv_more = False
                            investors = sent[i + 1]
                    except IndexError:
                        pass
                    try:
                        if sent[i - 1] not in sw and sent[i + 1] not in sw and not main_found:
                            main_found = True
                            investors = sent[i + 1]
                            target = sent[i - 1]
                    except IndexError:
                        pass

        # for it in res_names1:
        #     for i in range(len(it)):
        #         try:
        #             if it[i] == '->':
        #                 investors = it[i - 1]
        #                 target = it[i + 1]
        #             if it[i] == '<-':
        #                 investors = it[i + 1]
        #                 target = it[i - 1]
        #         except IndexError:
        #             pass
        #     if (investors != 'NaN') and (target != 'NaN'):
        #         break

        # nosochek bil tut
        price = clear(res_money)[0]
        percent = 'NaN'
        sphere = 'NaN'
        country = 'Россия'
        response = investors not in sw and target not in sw and investors != target
        if info:
            print(LONG)
            print(article)
            print(res_names)
            print(cL_res_names1)
            print(res_names1)
            print('------')
            print('targ:', target)
            print('inv:', investors)
            print('price:', price)
            print(LONG)
        return response, target, price, percent, investors, sphere, country
    else:
        pass
        # ner_model = build_model(configs.ner.ner_rus_bert, download=True)
        #
        # ner_model(['Bob Ross lived in Florida'])

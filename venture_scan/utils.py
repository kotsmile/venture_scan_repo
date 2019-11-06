from venture_scan.data_processing import load_pickle, save_pickle

import requests
import webbrowser
from pandas import DataFrame


def send(msg):
    token = '975456275:AAGqcqmWa9miwQrpBn2VqA3cZs34IFEEYmI'
    id = 182301431
    send_text = f'https://api.telegram.org/bot{token}/sendMessage?chat_id={id}&text={msg}'
    requests.get(send_text)


def marking(table_path, per=True, start=0):
    if per:

        new_table = load_pickle(table_path + 'm.pck')
        print(len(new_table['good']))
        all = 0
        plus = 0
        rees = 0
        for valid_t, valid_p, valid_i, art, good in zip(new_table['valid_target'], new_table['valid_price'],
                                                        new_table['valid_investors'], new_table['art_main'],
                                                        new_table['good']):
            if good:
                all += 1
                rees += art
                if valid_t + valid_i == 2:
                    plus += 1
        print(plus / all)
        print(rees / all)

    else:
        if start != 0:
            new_table = load_pickle(table_path + 'm.pck')
        else:
            new_table = {'target': [],
                         'price': [],
                         'investors': [],
                         'link': [],
                         'valid_target': [],
                         'valid_price': [],
                         'valid_investors': [],
                         'art_main': [],
                         'good': []}
        table = load_pickle(table_path + '.pck')

        for tar, price, inv, link in zip(table['target'], table['price'], table['investors'], table['link']):
            if start != 0:
                if link in new_table['link']:
                    continue
            # print('\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n')
            print(tar, price, inv, link, sep='\t', end='\t')
            webbrowser.open(link)
            ans = input().split()
            if not ans:
                continue
            if ans[0] == 'f' or ans[0] == '`':
                break

            if ans[0] == 'z':
                ans = [0, 0, 0, 0, 0]
            if ans[0] == 'o':
                ans = [1, 1, 1, 1, 1]
            f = True
            while f:
                try:
                    valid_target = int(ans[0])
                    valid_price = int(ans[1])
                    valid_investors = int(ans[2])
                    art_main = int(ans[3])
                    good = int(ans[4])
                    f = False
                except IndexError:
                    ans = input().split()
                    continue
            if valid_target == 'f':
                break
            new_table['target'].append(tar)
            new_table['price'].append(price)
            new_table['investors'].append(inv)
            new_table['link'].append(link)
            new_table['valid_target'].append(valid_target)
            new_table['valid_price'].append(valid_price)
            new_table['valid_investors'].append(valid_investors)
            new_table['art_main'].append(art_main)
            new_table['good'].append(good)

        save_pickle(new_table, f'{table_path}m.pck')

        df = DataFrame.from_dict(new_table)
        df.to_csv(f'{table_path}m.csv')

        marking(table_path, per=True)

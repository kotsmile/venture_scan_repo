import web_parsing_tool as webtool
import pickle
import pandas as pd
import time
import random


def pretty_date(date):
    return f'{date[0]}/{date[1]}/{date[2]}'


def firmma_getter():
    def page_number(index):
        return f'http://firrma.ru/data/?PAGEN_1={index}'

    config_titles = webtool.concatenate_config(*[
        webtool.tag_builder(
            tag_name='a',
            attribute='class',
            content='title',
            status=True,
            matching='some'
        ),
        webtool.tag_builder(
            tag_name='a',
            extra='else',
            formatting=lambda t: t.text
        )
    ])
    titles = []
    t1 = time.time()

    titles += webtool.web_parse(url=page_number(1), config=config_titles)[0]
    t2 = time.time()
    for i in range(2, 770):
        titles += webtool.web_parse(url=page_number(i), config=config_titles)[0]
        print(i * 100 / 770, 'time left:', (t2 - t1) * (770 - i), 'secs')

    return titles


def firmma_by_title():
    def page_number(index):
        return f'http://firrma.ru/data/?PAGEN_1={index}'

    config_titles = webtool.concatenate_config(*[
        webtool.tag_builder(
            tag_name='a',
            attribute='class',
            content='title',
            status=True,
            matching='some'
        ),
        webtool.tag_builder(
            tag_name='a',
            extra='else',
            formatting=lambda t: t.text
        )
    ])

    for i in range(2, 770):
        titles = webtool.web_parse(url=page_number(i), config=config_titles)[0]
        for t in titles:
            yield t


def all_vc(start=1, random_time=lambda: random.random() * 1.5 + 0.5):
    def get_page(index):
        return f'https://vc.ru/marketing/{index}'

    config_time = webtool.concatenate_config(*[
        webtool.tag_builder(
            tag_name='time',
            attribute='class',
            content='time',
            status=True,
            matching='some'
        ),
        webtool.tag_builder(
            tag_name='time',
            extra='else',
            formatting=lambda t: t['title']
        )
    ])
    config_title = webtool.concatenate_config(*[
        webtool.tag_builder(
            tag_name='h1',
            attribute='itemprop',
            content='headline',
            status=True,
            matching='some'
        ),
        webtool.tag_builder(
            tag_name='h1',
            extra='else',
            formatting=lambda t: t.text
        )
    ])
    config_type = webtool.concatenate_config(*[
        webtool.tag_builder(
            tag_name='a',
            attribute='class',
            content='entry_header__subsite__name',
            status=True,
            matching='some'
        ),
        webtool.tag_builder(
            tag_name='a',
            extra='else',
            formatting=lambda t: t.text
        )
    ])
    config_article = {
        'text': {
            'p': {'_extra': ('_nothing', lambda t: t.text)}
        },
        'link': {'p': {'_extra': ('_all', None)}},
        'theme_tag': {}
    }

    i = start
    while i <= 83727:
        i += 1
        time.sleep(random_time())

        try:
            date = webtool.web_parse(url=get_page(i), config=config_time)[0][0][:10].split('.')
            title = webtool.web_parse(url=get_page(i), config=config_title)[0][0].strip()
            article = ''.join(webtool.web_parse(url=get_page(i), config=config_article)[0]).replace('\n', '[NL]')
            link = get_page(i)

            yield (title, article, date, link)
        except IndexError:
            print(f'bad link {get_page(i)}')
            continue


def vc_by_title(random_time=lambda: random.random() * 1.5 + 0.5):
    def get_page(index):
        return f'https://vc.ru/marketing/{index}'

    config_title = webtool.concatenate_config(*[
        webtool.tag_builder(
            tag_name='h1',
            attribute='itemprop',
            content='headline',
            status=True,
            matching='some'
        ),
        webtool.tag_builder(
            tag_name='h1',
            extra='else',
            formatting=lambda t: t.text
        )
    ])
    i = 1
    while True:
        i += 1
        time.sleep(random_time())

        try:
            title = webtool.web_parse(url=get_page(i), config=config_title)[0][0].strip()
            yield title
        except IndexError:
            continue


def vc_getter(path_to_dump, info_print=True, good=True, need=78840, start=12199,
              random_time=lambda: random.random() * 1.5 + 0.5):
    def get_page(index):
        return f'https://vc.ru/marketing/{index}'

    config_time = webtool.concatenate_config(*[
        webtool.tag_builder(
            tag_name='time',
            attribute='class',
            content='time',
            status=True,
            matching='some'
        ),
        webtool.tag_builder(
            tag_name='time',
            extra='else',
            formatting=lambda t: t['title']
        )
    ])
    config_title = webtool.concatenate_config(*[
        webtool.tag_builder(
            tag_name='h1',
            attribute='itemprop',
            content='headline',
            status=True,
            matching='some'
        ),
        webtool.tag_builder(
            tag_name='h1',
            extra='else',
            formatting=lambda t: t.text
        )
    ])
    config_type = webtool.concatenate_config(*[
        webtool.tag_builder(
            tag_name='a',
            attribute='class',
            content='entry_header__subsite__name',
            status=True,
            matching='some'
        ),
        webtool.tag_builder(
            tag_name='a',
            extra='else',
            formatting=lambda t: t.text
        )
    ])
    config_article = {
        'text': {
            'p': {'_extra': ('_nothing', lambda t: t.text)}
        },
        'link': {'p': {'_extra': ('_all', None)}},
        'theme_tag': {}
    }

    dump = {'date': [], 'title': [], 'article': [], 'link': []}

    # key_words = ['привлек', 'фонда', 'венчурн', 'влож', 'вкла', 'инвест']

    success, attempts = 0, 0
    amount = 78840
    i = start

    while i <= amount:
        try:
            time.sleep(random_time())

            try:
                date = webtool.web_parse(url=get_page(i), config=config_time)[0][0][:10].split('.')
                title = webtool.web_parse(url=get_page(i), config=config_title)[0][0].strip()
                article = ''.join(webtool.web_parse(url=get_page(i), config=config_article)[0])
                type_ = webtool.web_parse(url=get_page(i), config=config_type)[0][0]

                if success >= need:
                    break
                if info_print:
                    print(title)
                    print(f'{i * 100 // amount}%, success: {success}, {type_}, {get_page(i)}')

                ans = True
                # for w in title.split(' '):
                #     for kw in key_words:
                #         if w.startswith(kw):
                #             ans = True

                if ans == good:
                    with open(path_to_dump, 'a') as f:
                        f.write(f'{title.replace(";", ",")};{get_page(i)}\n')
                    # dump['date'].append(date)
                    # dump['title'].append(title)
                    # dump['article'].append(article)
                    # dump['link'].append(get_page(i))
                    success += 1

                i += 1
                attempts = 1
            except IndexError:
                if info_print:
                    print(f'[problem {attempts}] {i * 100 // amount}%, success: {success}, {get_page(i)}')
                attempts += 1
                if attempts > 1:
                    i += 1
                    attempts = 0
                    continue

        except KeyboardInterrupt:
            break

    return dump


def update_dump(path, spec=False, start=0, good=True):
    if spec:
        dump = {'date': [], 'title': [], 'article': [], 'link': []}
        sources = [
            vc_getter
        ]

        for source in sources:
            i = 1
            for title in source(need=500, start=start, good=good)['title']:
                with open(path, 'a') as f:
                    f.write(f'__label__other {title}\n')

    else:
        dump = {'date': [], 'title': [], 'article': [], 'link': []}
        sources = [
            vc_getter
        ]

        for source in sources:
            for k, v in source().items():
                dump[k] += v

        with open(f'{path}.pck', 'wb') as f:
            pickle.dump(dump, f)

        df = pd.DataFrame.from_dict(dump)
        df.to_csv(f'{path}.csv')

        # with open(f'{path}.pck', 'w') as f:
        #     f.write('date,title,article,link\n')
        #     for d, t, a, l in zip(dump['date'], dump['title'], dump['article'], dump['link']):
        #         f.write(f"'{pretty_date(d)}','{t}','{a}','{l}'\n")

        print(f'all files saved in {path}')
        return dump

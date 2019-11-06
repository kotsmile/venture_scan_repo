import web_parsing_tool.utils as utils
from web_parsing_tool.configuration import configs
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
import re

"""
---format of config---

config =    {
                'text':
                    {
                        'tag_name1':
                        {
                            'attribute_name1': ['content', True, '_all'],
                            'attribute_name2': ['content', False, '_some'],
                            'attribute_name3': ['_no_matter', False],
                            '_extra': ('_else', formatting_function())
                        },
                        'tag_name2:
                        {
                            '_extra': ('_nothing', formatting_function())
                        }
                        'tag_name3:
                        {
                            'attribute_name3': ['_no_matter', False],
                            '_extra': ('_only', formatting_function())
                        }
                        'tag_name4:
                        {
                            '_extra': ('_all', formatting_function())
                        }
                    }
                'link':
                    {
                        'parent_tag_name1':
                        {
                            'attribute_name1': ['content', True, '_all'],
                            'attribute_name2': ['content', False, '_some'],
                            'attribute_name3': ['_no_matter', False],
                            '_extra': ('_else', formatting_function())
                        },
                        'parent_tag_name2:
                        {
                            '_extra': ('_nothing', formatting_function())
                        },
                        'parent_tag_name3:
                        {
                            'attribute_name3': ['_no_matter', False],
                            '_extra': ('_only', formatting_function())
                        },
                        'parent_tag_name4:
                        {
                            '_extra': ('_all', formatting_function())
                        }
                    }
                'theme_tag': {
                    WIP
                }
            }

_extra:
    _only   : only this structure of tag
    _else   : this structure and something else
    _all    : everything, without describing attributes 
    _nothing: empty, like <tag>smth</tag>

attribute settings:
    content:
        strings separated with comma (can use @ ["@exm" == "smthexmevth"]): names of attribute
        _no_matter: no matter what inside
    status:
        True: access
        False: deny
    matching:
        _all: everything is same
        _some: some of them 

"""


def exist(url):
    domain = '{uri.scheme}://{uri.netloc}/'.format(uri=urlparse(url))
    return domain in configs.keys()


def web_parse(url=None, config=None, attempts=0, anti_block=False, text=False, html_print=False):
    """
    :param url: url
    :param config: {configuration}
    :param attempts: amount of attempts to connect
    :param anti_block: on/off
    :param text: convert text to clear text
    :param html_print: print html from your page
    :return: ([texts], [links], [theme_tags])
    """
    if not url:
        print('[Error] Expected url')
        return [], [], [], -1
    if not config:
        print('[Error] Expected configuration')
        return [], [], [], -1

    html = 'none'
    try:
        if anti_block:
            headers = {
                'User-Agent': f'{utils.get_random_ua()}',
                'Referer': urljoin(url, ''),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
            }
            html = requests.get(url, headers=headers)
        else:
            html = requests.get(url)

    except requests.exceptions.ConnectionError:
        if attempts < 100:
            print('Bad connection...')
            time.sleep(5.0)
            return web_parse(url=url, config=config, attempts=attempts + 1, anti_block=anti_block)
        else:
            print('Cannot to connect to the server')
            return [], [], [], -1

    soup = BeautifulSoup(html.text, 'html.parser')
    if html_print:
        print(soup.prettify())

    # remove scripts and styles code
    for script in soup(['script', 'style']):
        script.extract()

    raw_texts, links, theme_tags = [], [], []

    for tag in soup():
        try:
            # link part
            if tag.name == 'a':
                f_func, response = utils.check_link(link=tag, link_config=config['link'])
                if response:
                    links.append(urljoin(url, tag.get('href')))

            # text part

            f_func, response = utils.check_tag(tag=tag, tag_config=config['text'])
            if response:
                raw_texts.append(f_func(tag))

        except KeyError:
            print('[Error] Bad configuration')

    texts = []
    if text:
        for t in raw_texts:
            response, clear_text = utils.to_text(t)
            if response:
                texts.append(clear_text)
    else:
        texts = raw_texts

    return texts, links, theme_tags, 0


def fix_parse(url, silence=False, anti_block=False):
    domain = '{uri.scheme}://{uri.netloc}/'.format(uri=urlparse(url))
    try:
        result = web_parse(url=url, config=configs[domain], anti_block=anti_block, text=True)
    except KeyError:
        if not silence:
            print('[Error] Url not found')
        return [], [], [], -1
    return result


def random_parse(url, anti_block=False):
    # check for pdf and jpg files
    pat = re.compile(r'.+\.(([pP][dD][fF])|([jJ][pP][gG]))')
    if pat.match(url):
        return [], [], [], -1

    # maybe fix source
    result = fix_parse(url, silence=True, anti_block=anti_block)
    if result[3] == 0:
        return result[0], result[1], result[2], utils.sentence_score(' '.join(result[0]))

    results = []
    for k, v in configs.items():
        w = web_parse(url, config=v, anti_block=anti_block)
        new_text = [utils.to_text(t)[1] for t in w[0] if utils.to_text(t)[0]]
        results.append((new_text, w[1], w[2], utils.sentence_score(' '.join(new_text))))

    results = sorted(results, key=lambda it: it[3], reverse=True)

    return results[0]

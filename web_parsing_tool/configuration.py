from web_parsing_tool.utils import create_trash_func
from web_parsing_tool.utils import enter

WIKI = {
    'text': {
        'h1': {'class': ['firstHeading', True, '_some'], '_extra': ('_else', enter)},
        'span': {'class': ['mw-headline', True, '_some'], '_extra': ('_else', enter)},
        'p': {'_extra': ('_nothing', create_trash_func(trash=['sup'], format_=enter))}
    },
    'link': {'p': {'_extra': ('_all', None)}},
    'theme_tag': {}
}

MEDIUM = {
    'text': {
        'h1': {'class': ['graf--h1', True, '_some'], '_extra': ('_else', enter)},
        'h2': {'class': ['graf--h2', True, '_some'], '_extra': ('_else', enter)},
        'h3': {'class': ['graf--h3', True, '_some'], '_extra': ('_else', enter)},
        'p': {'class': ['graf--p', True, '_some'], '_extra': ('_else', enter)},
    },
    'link': {'p': {'_extra': ('_all', None)}},
    'theme_tag': {}
}

CNN = {
    'text': {
        'div': {'class': ['Paragraph__component', True, '_some'],
                '_extra': ('_else', enter)},
    },
    'link': {'div': {'class': ['Paragraph__component', True, '_some'], '_extra': ('_else', None)}},
    'theme_tag': {}
}

BBC = {
    'text': {
        'h1': {'class': ['story-body__h1', True, '_some'], '_extra': ('_else', enter)},
        'p': {'_extra': ('_nothing', enter)}
    },
    'link': {'p': {'_extra': ('_all', None)}},
    'theme_tag': {}
}

HABR = {
    'text': {
        'h1': {'class': ['post__title', True, '_some'], '_extra': ('_else', enter)},
        'div': {'class': ['post__text', True, '_some'], '_extra': ('_else', enter)}
    },
    'link': {'div': {'class': ['post__text', True, '_some'],
                     '_extra': ('_else', create_trash_func(trash=['img'], format_=enter))}},
    'theme_tag': {}
}

FORBES = {
    'text': {
        'p': {'_extra': ('_nothing', enter)}
    },
    'link': {'p': {'_extra': ('_all', None)}},
    'theme_tag': {}
}

RIA = {
    'text': {
        'div': {'class': ['article__text', True, '_some'],
                '_extra': ('_else', enter)},
        'h1': {'class': ['article__title', True, '_some'], '_extra': ('_else', enter)}
    },
    'link': {'div': {'class': ['article__text', True, '_some'], '_extra': ('_else', None)}},
    'theme_tag': {}
}

CNBC = {
    'text': {
        'div': {'class': ['group', True, '_some'],
                '_extra': ('_else', enter)},
        'h1': {'class': ['title', True, '_some'],
               '_extra': ('_else', enter)}
    },
    'link': {'p': {'_extra': ('_all', None)}},
    'theme_tag': {}
}

MARKET = {
    'text': {
        'p': {'_extra': ('_nothing', enter)},
        'h6': {'_extra': ('_nothing', enter)}
    },
    'link': {'p': {'_extra': ('_all', None)}},
    'theme_tag': {}
}

# universal parameters

UNIV_P_H = {
    'text': {
        'p': {'_extra': ('_all', enter)},
        'h1': {'_extra': ('_all', enter)},
        'h2': {'_extra': ('_all', enter)},
        'h3': {'_extra': ('_all', enter)}
    },
    'link': {'p': {'_extra': ('_all', None)}},
    'theme_tag': {}
}

UNIV_DIV = {
    'text': {
        'div': {'class': ['@text, @paragraph, @content', True, '_some'], '_extra': ('_else', enter)}
    },
    'link': {'div': {'class': ['@text, @paragraph, @content', True, '_some'], '_extra': ('_else', None)}},
    'theme_tag': {}
}

configs = {
    'https://en.wikipedia.org/': WIKI,
    'https://medium.com/': MEDIUM,
    'https://medium.freecodecamp.org/': MEDIUM,
    'https://edition.cnn.com/': CNN,
    'https://www.bbc.com/': BBC,
    'https://habr.com/': HABR,
    'https://www.forbes.com/': FORBES,
    'https://ria.ru/': RIA,
    'https://www.cnbc.com/': CNBC,
    'https://www.marketwatch.com/': MARKET,
    'universe_div': UNIV_DIV,
    'universe_p': UNIV_P_H
}


def tag_builder(tag_name=None, attribute=None, content=None, status=None, matching=None, extra=None, formatting=None):
    """
    Function to create tag config
    :param tag_name: (str) name of tag
    :param attribute: (str) attributes
    :param content: (str) consist of
    :param status: (bool) accept or not
    :param matching: (str) matching configuration
        all: everything is same
        some: some of them
    :param extra: (str) extra configuration
        only   : only this structure of tag
        else   : this structure and something else
        all    : everything, without describing attributes
        nothing: empty, like <tag>smth</tag>
    :param formatting:  (def) formatting function
    :return: (list) tag config
    """
    if extra:
        return [tag_name, '_extra', ('_' + extra, formatting)]
    else:
        return [tag_name, attribute, [content, status, '_' + matching]]


def concatenate_config(*tags):
    """
    concatenate tags to final config
    :param tags: (list) of tags
    :return: (dict) config
    """
    final = dict()
    for t, a, d in tags:
        try:
            final[t][a] = d
        except KeyError:
            final[t] = {a: d}
    return {
        'text': final,
        'link': {'p': {'_extra': ('_nothing', None)}},
        'theme_tag': {}
    }


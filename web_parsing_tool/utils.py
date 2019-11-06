import re


# def get_random_ua():
#     random_ua = ''
#     ua_file = './web_parsing_tool/data/ua_file.txt'
#     with open(ua_file, 'r') as f:
#         lines = f.readlines()
#     if len(lines) > 0:
#         prng = np.random.RandomState()
#         index = prng.permutation(len(lines) - 1)
#         idx = np.asarray(index, dtype=np.integer)[0]
#         random_proxy = lines[int(idx)]
#         random_ua = random_proxy
#     return str(random_ua).strip()


def create_trash_func(gold=None, trash=None, format_=lambda s: s):
    """
    Create trash function to delete unneeded tags and find need, and convert to foramt
    :param gold: (list) needed tags
    :param trash: (list) unneeded tags
    :param format_: (def) formatting function
    :return: (def) trash function
    """
    if trash:
        def temp(tag):
            for t in tag():
                if t.name in trash:
                    t.extract()
            return format_(tag)

    elif gold:
        def temp(tag):
            for t in tag():
                if t.name not in gold:
                    t.extract()
            return format_(tag)

    return temp


def to_text(text, min_=5):
    """
    Prettify random text
    :param text: (str) raw text
    :param min_: (int) minimal amount of words
    :return: ((bool) enough words in text, (str) pretty text)
    """
    # clean text
    text = remove_doubles(text)

    # check for length < min_
    if len(text) < min_:
        return False, ''

    # check for symbols in sentences
    if not re.compile(r'''[^a-zA-Zа-яА-Я0-9-–.!?,:;'()«»]''').match(text):
        return False, ''

    return True, text.strip()


def enter(s):
    return '\n\n' + s.text + '\n\n'


def sentence_score(text):
    """
    Calculate score of text
    :param text: (str) text
    :return: (int) score of text
    """
    sentence_pat = re.compile(r"[A-ZА-Я][^.?!]+[.!?]")
    res = len(re.findall(sentence_pat, text))

    return res


def remove_doubles(text):
    """
    Remove double '\n' and '\s' in text
    :param text: (str) text
    :return: (str) clear text
    """
    text = re.sub(r'\n+', ' ', text)
    text = re.sub(r' +', ' ', text)

    return text


def none():
    pass


def check_tag(tag=None, tag_config=None):
    """
    Tag verification
    :param tag: (obj) tag
    :param tag_config: (dict) tag config
    :return: (def) format function, (bool) response
    """
    name = tag.name

    # check for name
    if name not in tag_config.keys():
        return none, False

    extra = tag_config[name]['_extra'][0]
    func = tag_config[name]['_extra'][1]

    response = False

    for k, v in tag_config[name].items():

        if k == '_extra' and extra != '_all' and extra != '_nothing':
            continue

        content = v[0]
        status = v[1]

        if extra == '_else':

            if k in tag.attrs.keys():
                if content == '_no_matter':
                    response = status

                else:
                    dc = [i.strip() for i in content.split(',')]
                    if v[2] == '_some':
                        # print(tag_config)
                        g = tag[k]
                        if isinstance(tag[k], str):
                            g = [tag[k]]
                        if len(set(dc) & set(g)) > 0:
                            response = status
                        else:
                            my_attr = {s.strip() for s in set(dc)}
                            sub = [s[1:] for s in my_attr if s[0] == '@']
                            res = False
                            for s in tag[k]:
                                for s_sub in sub:
                                    res = res or s_sub.lower() in s.lower()
                            response = status and res

                    elif v[2] == '_all':
                        if status:
                            response = set(dc) == set(tag[k])

                        else:
                            response = not set(dc) == set(tag[k])
        elif extra == '_nothing':
            response = not tag.attrs

        elif extra == '_all':
            response = True

        elif extra == '_only':
            if k in tag.attrs.keys():
                if content == '_no_matter':
                    response = status

                else:
                    dc = [i.strip() for i in content.split(',')]
                    if v[2] == '_some':
                        response = len(set(dc) & set(tag[k])) > 0 and status

                    elif v[2] == '_all':
                        if status:
                            response = set(dc) == set(tag[k])

                        else:
                            response = not set(dc) == set(tag[k])
            else:
                response = False

    return func, response


def check_link(link=None, link_config=None):
    """
    Tag verification
    :param link: (obj) tag
    :param link_config: (dict) tag config
    :return: (def) format function, (bool) response
    """
    parent_tag = link.parent
    return check_tag(tag=parent_tag, tag_config=link_config)

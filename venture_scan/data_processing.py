import pickle


def load_pickle(path):
    """
    Load pickle object .pck
    :param path: (str) path to file without .pck
    :return: (obj)
    """
    try:
        return pickle.load(open(path + '.pck', 'rb'))
    except FileNotFoundError:
        return None


def save_pickle(obj, path):
    """
    Save object
    :param obj: (obj)
    :param path: (str) path to object
    :return: none
    """
    with open(path + '.pck', 'wb') as f:
        pickle.dump(obj, f)

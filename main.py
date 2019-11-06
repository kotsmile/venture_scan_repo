from venture_scan.production import test_check_title_part, new_dump
from venture_scan.utils import send
from venture_scan.data_processing import load_pickle
from venture_scan.components.check_title import create_trained_check_title_model

from paths import *


def main():
    # test_check_title_part(path_to_ft_model=PATH_TO_FT_MODEL, cross_val=True)
    # create_trained_check_title_model(PATH_TO_FT_MODEL)
    new_dump(PATH_TO_FT_MODEL)


if __name__ == '__main__':
    main()

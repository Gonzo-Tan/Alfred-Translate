import os
from youdao_translate import yd_search

if __name__ == '__main__':
    platform = os.getenv('PLATFORM')

    if platform == "YD":
        yd_search()

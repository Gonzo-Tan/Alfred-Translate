# -*- coding: utf-8 -*-
import sys
import uuid
import urllib
import urllib2
import hashlib
import json
import time
import argparse
from alfred.feedback import Feedback
import os

reload(sys)
sys.setdefaultencoding('utf-8')

YOUDAO_URL = 'https://openapi.youdao.com/api'

DEFAULT_HEADERS = {'Content-Type': 'application/x-www-form-urlencoded'}


def encrypt(signStr):
    hash_algorithm = hashlib.sha256()
    hash_algorithm.update(signStr.encode('utf-8'))
    return hash_algorithm.hexdigest()


def truncate(q):
    if q is None:
        return None
    q_utf8 = q.decode("utf-8")
    size = len(q_utf8)
    return q_utf8 if size <= 20 else q_utf8[0:10] + str(size) + q_utf8[size - 10:size]


def do_request(data):
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    return requests.post(YOUDAO_URL, data=data, headers=headers)


def _request(path, params=None, method='GET', data=None, headers=None):
    params = params or {}
    headers = headers or {}
    if params:
        url = path + '?' + urllib.urlencode(params)
    else:
        url = path

    request = urllib2.Request(url, data, headers)
    request.get_method = lambda: method
    response = urllib2.urlopen(request)
    return response.read()


def output(yd_res):
    # print yd_res
    feedback = Feedback()

    # 添加默认的结果
    phonetic = ""
    phonetic2 = ""
    if "basic" in yd_res:
        if "phonetic" in yd_res["basic"]:
            phonetic = " 英 [" + yd_res["basic"]["phonetic"] + "]"
        if "us-phonetic" in yd_res["basic"]:
            phonetic2 = " 美 [" + yd_res["basic"]["us-phonetic"] + "]"

    trs_str = ''
    if "translation" in yd_res:
        for trs in yd_res["translation"]:
            trs_str = trs_str + trs + '; '
    else:
        trs_str = '无结果'

    title = trs_str + phonetic + phonetic2
    feedback.addItem(title=title, subtitle=yd_res["query"])

    if "basic" in yd_res:
        if "explains" in yd_res["basic"]:
            for explain in yd_res["basic"]["explains"]:
                item = {
                    "title": explain,
                    "arg": explain
                }
                feedback.addItem(**item)

    if "web" in yd_res:
        for web in yd_res["web"]:
            web_str = ''
            for web_i in web["value"]:
                web_str = web_str + web_i + "; "
            item = {
                "title": web_str,
                "subtitle": web["key"],
                "arg": web_str
            }
            feedback.addItem(**item)

    feedback.output()


def search(word, appKey, appSecretppKey):
    feedback = Feedback()

    q = word

    data = {}
    data['from'] = 'auto'
    data['to'] = 'auto'
    data['signType'] = 'v3'
    curtime = str(int(time.time()))
    data['curtime'] = curtime
    salt = str(uuid.uuid1())
    signStr = appKey + truncate(q) + salt + curtime + appSecretppKey
    sign = encrypt(signStr)
    data['appKey'] = appKey
    data['q'] = q
    data['salt'] = salt
    data['sign'] = sign
    data['vocabId'] = "您的用户词表ID"

    response = _request(YOUDAO_URL, '', 'POST', urllib.urlencode(data), DEFAULT_HEADERS)
    result = json.loads(response)
    # print response
    # print 'test'
    # result = {'translation': 'translation', 'query': 'query'}

    # res_word = str(result['translation'][0])
    # pron = str(result['query'])
    # title = "%s [%s]" % (res_word, pron)

    # print hasattr(result, "translation")
    # print "translation" in result

    # trs_str = ''
    # if "translation" in result:
    #     for trs in result["translation"]:
    #         trs_str = trs_str + trs + '; '
    # else:
    #     trs_str = '无结果'
    #
    # web_str = ''
    # if "web" in result:
    #     for web in result["web"]:
    #         for web_i in web["value"]:
    #             web_str = web_str + web_i + "; "
    # else:
    #     web_str = '无'
    #
    # phonetic = ""
    # if "basic" in result and "phonetic" in result["basic"]:
    #     phonetic =  " [" + result["basic"]["phonetic"] + "]"
    #
    # item = {
    #     "title": word + ": " + trs_str + phonetic,
    #     "subtitle": "网络释义: " + web_str,
    #     "arg": result["translation"][0]
    # }
    #
    # # feedback.addItem(title=title, arg=res_word)
    # feedback.addItem(**item)
    # feedback.output()

    output(result)



def yd_search():
    appKey = os.getenv('YD_APP_KEY')
    appSecretppKey = os.getenv('YD_APP_SECRET_KEY')

    parser = argparse.ArgumentParser()
    parser.add_argument('--search', nargs='?', type=str)
    args = parser.parse_args()

    if args.search:
        search(args.search, appKey, appSecretppKey)
    else:
        raise ValueError()


if __name__ == '__main__':
    yd_search()

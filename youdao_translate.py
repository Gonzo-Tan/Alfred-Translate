# -*- coding: utf-8 -*-
import sys
import uuid
from urllib import request, parse
import hashlib
import json
import time
import argparse
from alfred.feedback import Feedback
import os
import ssl
#import requests

from imp import reload

reload(sys)

ssl._create_default_https_context = ssl._create_unverified_context

YOUDAO_URL = 'https://openapi.youdao.com/api'

DEFAULT_HEADERS = {'Content-Type': 'application/x-www-form-urlencoded'}


def encrypt(signStr):
    hash_algorithm = hashlib.sha256()
    hash_algorithm.update(signStr.encode('utf-8'))
    return hash_algorithm.hexdigest()


def truncate(q):
    if q is None:
        return None
    size = len(q)
    return q if size <= 20 else q[0:10] + str(size) + q[size - 10:size]


#def do_request(data):
    #return requests.post(YOUDAO_URL, data=data, headers=DEFAULT_HEADERS)


def _request(path, params=None, method='GET', data=None, headers=None):
    params = params or {}
    headers = headers or {}
    if params:
        url = path + '?' + parse.urlencode(params)
    else:
        url = path
    data = parse.urlencode(data).encode('utf-8')
    req = request.Request(url, data=data, headers=headers, method=method)
    res = request.urlopen(req, timeout=10).read()
    return res


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
    trs_0 = ''
    if "translation" in yd_res:
        for trs in yd_res["translation"]:
            trs_str = trs_str + trs + '; '
        trs_0 = yd_res["translation"][0]
    else:
        trs_str = '无结果'

    title = trs_str + phonetic + phonetic2
    feedback.addItem(title=title, subtitle=yd_res["query"], arg=trs_0)

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
                "arg": web_str,
                "icon": "imgs/net.png"
            }
            feedback.addItem(**item)

    feedback.output()


def search(word, appKey, appSecretppKey):
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

    response = _request(YOUDAO_URL, data=data, method="POST", headers=DEFAULT_HEADERS)
    #response = do_request(data)
    result = json.loads(response)
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
    search("love", "6815d7d0d75ccd6b", "SNVjyMTLEwtbDGo84gHJ5aqZKEJvkzdU")

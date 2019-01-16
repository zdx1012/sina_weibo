#!/usr/bin/env python
# -*- coding: utf-8 -*-
# import redis
# import requests
# import time
#
# redis_obj = redis.Redis(host='127.0.0.1', port=6379, db=0, decode_responses=True)
#
#
# def reset_ip():
#     c = requests.get('http://piping.mogumiao.com/proxy/api/get_ip_bs?appKey=54382bb1c7bf4329946a492debdadf88&count=1&expiryDate=0&format=2&newLine=3')
#     print(c.text, "----")
#     ip = c.text.replace('\r', '').replace('\n', '').strip(' ')
#     redis_obj.set('kkk', ip)
#
#
# if __name__ == '__main__':
#     while True:
#         ip = redis_obj.get('kkk')
#         proxies = {
#             'http': 'http://%s' % ip,
#             'https': 'http://%s' % ip
#         }
#         req_headers = {
#             "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36",
#         }
#         try:
#             c = requests.get('https://m.weibo.cn/api/container/getIndex?type=uid&value=1755370981', headers=req_headers, proxies=proxies,
#                              timeout=8).status_code
#             print(c)
#             if c != 200:
#                 reset_ip()
#         except BaseException as e:
#             print(e.args)
#             reset_ip()
#             print('reset')
#         time.sleep(1)

import redis
import requests
import time
import json
import datetime
redis_obj = redis.Redis(host='127.0.0.1', port=6379, db=0, decode_responses=True)


def reset_ip():
    c = requests.get('http://piping.mogumiao.com/proxy/api/get_ip_bs?appKey=54382bb1c7bf4329946a492debdadf88&count=1&expiryDate=0&format=1&newLine=3')
    data = json.loads(c.text)
    if data['code'] == "0":
        print(datetime.datetime.now(),data['msg'])
        for tmp in data['msg']:
            redis_obj.sadd('ip_set', tmp['ip'] + ":" + tmp['port'])


if __name__ == '__main__':
    reset_ip()
    while True:
        try:
            ip = redis_obj.srandmember('ip_set', 1)[0]
        except BaseException as e:
            reset_ip()
            ip = redis_obj.srandmember('ip_set', 1)[0]
        proxies = {
            'http': 'http://%s' % ip,
            'https': 'http://%s' % ip
        }
        req_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36",
        }
        try:
            c = requests.get('https://m.weibo.cn/api/container/getIndex?type=uid&value=1755370981', headers=req_headers, proxies=proxies,
                             timeout=8).status_code
            if c != 200:
                redis_obj.srem('ip_set', ip)
        except BaseException as e:
            redis_obj.srem('ip_set', ip)
        if len(redis_obj.smembers('ip_set')) < 2:
            reset_ip()
        time.sleep(1)

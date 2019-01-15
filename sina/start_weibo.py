#!/usr/bin/env python
# -*- coding: utf-8 -*-
def get_format_datetime(datestr):
    import datetime
    import time
    now = datetime.datetime.now()
    ymd = now.strftime("%Y-%m-%d")
    y = now.strftime("%Y")
    newstr = datestr
    # newdate = now
    # if u"楼" in datestr:
    #     newstr = datestr.split(u"楼")[-1].strip()
    # if (u"今天" in newstr):
    #     mdate = time.mktime(time.strptime(ymd + newstr, '%Y-%m-%d今天 %H:%M'))
    #     newdate = datetime.datetime.fromtimestamp(mdate)
    # elif (u"月" in newstr):
    #     mdate = time.mktime(time.strptime(y + newstr, '%Y%m月%d日 %H:%M'))
    #     newdate = datetime.datetime.fromtimestamp(mdate)
    # elif (u"分钟前" in newstr):
    #     newdate = now - datetime.timedelta(minutes=int(newstr[:-3]))
    # elif (u"秒前" in newstr):
    #     newdate = now - datetime.timedelta(minutes=int(newstr[:-2]))
    # 以下为手机端
    if "-" in newstr:
        mdate = time.mktime(time.strptime(y + "-" + newstr, '%Y-%m-%d'))
        newdate = datetime.datetime.fromtimestamp(mdate)
    elif (u"昨天" in newstr):
        mdate = time.mktime(time.strptime(ymd + newstr, '%Y-%m-%d昨天 %H:%M'))
        newdate = datetime.datetime.fromtimestamp(mdate) - datetime.timedelta(days=1)
    elif (u"小时前" in newstr):
        newdate = now - datetime.timedelta(hours=int(newstr[:-3]))
    else:
        newdate = datetime.datetime.strptime(newstr, "%Y-%m-%d %H:%M")
    # 只保留 年-月-日
    return str(newdate)[:10]


if __name__ == '__main__':
    # print(get_format_datetime('01-13'))
    import os

    os.system('scrapy crawl weibo')

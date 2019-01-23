# -*- coding: utf-8 -*-
import json

import pymysql
import scrapy
import datetime
import time
from scrapy import Request
from lxml import etree
from sina.items import personInfo, SinaItem
from scrapy.spiders import Spider
from scrapy_redis.spiders import RedisSpider


class WeiboSpider(RedisSpider):
    name = 'weibo'
    allowed_domains = ['m.weibo.cn']
    find_more_user = True  # 是否爬取其他的用户信息以及微博
    redis_key = 'WeiboSpider:start_urls'

    # def start_requests(self):
    #     weibo_id = [1730077315, 1699432410, 2810373291, 1291477752, 3125046087, 1763582395]
    #     for wid in weibo_id:
    #         yield Request('https://m.weibo.cn/api/container/getIndex?type=uid&value=' + str(wid), callback=self.parse, dont_filter=True,
    #                       meta={'uid': str(wid)})

    # 解析个人信息
    def parse(self, response):
        data = response.text
        content = json.loads(data).get('data')
        if content:
            profile_image_url = content.get('userInfo').get('profile_image_url')
            description = content.get('userInfo').get('description')
            profile_url = content.get('userInfo').get('profile_url')
            verified = content.get('userInfo').get('verified')
            follow_count = content.get('userInfo').get('follow_count')
            followers_count = content.get('userInfo').get('followers_count')
            gender = content.get('userInfo').get('gender')
            urank = content.get('userInfo').get('urank')
            name = content.get('userInfo').get('screen_name')
            verified_type = content.get('userInfo').get('verified_type')
            verified_reason = content.get('userInfo').get('verified_reason')
            uid = content.get('userInfo').get('toolbar_menus')[0].get('params').get('uid')
            # 判断该微博用户是否爬取过一次他的关注的人，避免重复爬取
            # 举例： 张三关注李四，王老五也关注李四
            #       按照逻辑，则会爬取李四的信息2次
            #       那么后续李四关注的人也会爬取两次
            # conn = pymysql.connect(host='192.168.1.111', port=3306, db='weibo', user='zdx', passwd='asdf1234', charset='utf8')
            # cursor = conn.cursor()
            # sql = 'select * from sina_user where uid = %s and insert_time >= "%s" ' % (uid, '2019-01-23 15:37:02')
            # cursor.execute(sql)
            # result = cursor.fetchone()

            # if result is None:
            if int(followers_count) >= 200:
                # 保存用户
                person = personInfo()
                person["uid"] = uid
                person["name"] = name
                person["description"] = description
                person["follow_count"] = follow_count
                person["followers_count"] = followers_count
                person["profile_image_url"] = profile_image_url
                person["profile_url"] = profile_url
                person["verified"] = verified
                person["urank"] = urank
                person["gender"] = gender
                person["verified_type"] = verified_type
                person["verified_reason"] = verified_reason if verified_reason is not None else ""
                yield person

            # 爬取微博资料以及他关注的人
            for data in content.get('tabsInfo').get('tabs'):
                if (data.get('tab_type') == 'weibo'):
                    containerid = data.get('containerid')
                    weibo_list_url = 'https://m.weibo.cn/api/container/getIndex?type=uid&value=' + str(uid) + '&containerid=' + containerid + '&page=1'
                    yield Request(weibo_list_url, callback=self.parse_weibo_list, meta={'weibo_page': 1, 'containerid': containerid, 'uid': uid},
                                  dont_filter=True)

    # 解析微博列表
    def parse_weibo_list(self, response):

        # 取相关信息，方便爬取下一页
        # next_weibo_page = str(int(response.meta['weibo_page']) + 1)

        uid = response.meta['uid']
        containerid = response.meta['containerid']

        data = response.text
        content = json.loads(data).get('data')
        cards = content.get('cards')
        if (len(cards) > 0):
            # print("-----正在爬取第%s页-----" % str(response.meta['weibo_page']))

            for j in range(len(cards)):
                card_type = cards[j].get('card_type')
                # 微博
                # if card_type == 9:
                #     mblog = cards[j].get('mblog')
                #     attitudes_count = mblog.get('attitudes_count')  # 点赞数
                #     comments_count = mblog.get('comments_count')  # 评论数
                #     created_at = self.date_format(mblog.get('created_at'))  # 发布时间
                #     reposts_count = mblog.get('reposts_count')  # 转发数
                #     scheme = cards[j].get('scheme')  # 微博地址
                #     # 替换换行后 提取字符串
                #     text = etree.HTML(str(mblog.get('text')).replace('<br />', '\n')).xpath('string()')  # 微博内容
                #     pictures = mblog.get('pics')  # 正文配图，返回list
                #     pic_urls = []  # 存储图片url地址
                #     if pictures:
                #         for picture in pictures:
                #             pic_url = picture.get('large').get('url')
                #             pic_urls.append(pic_url)
                #     uid = response.meta['uid']
                #     # 保存数据
                #     sinaitem = SinaItem()
                #     sinaitem["uid"] = uid
                #     sinaitem["text"] = text
                #     sinaitem["scheme"] = scheme
                #     sinaitem["attitudes_count"] = attitudes_count
                #     sinaitem["comments_count"] = comments_count
                #     sinaitem["created_at"] = created_at
                #     sinaitem["reposts_count"] = reposts_count
                #     sinaitem["pictures"] = pic_urls
                #     yield sinaitem
                #     tmp_time = created_at
                # 关注信息
                if card_type == 11 and self.find_more_user:
                    # 获取他关注的人的地址
                    # https://m.weibo.cn/p/index?containerid=231051_-_followers_-_1195354434_-_1042015%3AtagCategory_050&luicode=10000011&lfid=1076031195354434 查看该网页的请求过程

                    fllow_base_url = str(cards[j]['card_group'][0]['scheme']).replace('https://m.weibo.cn/p/index?',
                                                                                      'https://m.weibo.cn/api/container/getIndex?') + "&page="
                    first_url = fllow_base_url + str(1)
                    # print('first_url:', first_url)
                    yield Request(url=first_url, callback=self.parse_fllow, meta={'follow_page': 1, 'base_url': fllow_base_url},
                                  dont_filter=True)
            # 下一页链接
            # weibo_list_url = 'https://m.weibo.cn/api/container/getIndex?type=uid&value=' + uid + '&containerid=' + containerid + '&page=' + next_weibo_page
            # response.meta['weibo_page'] = next_weibo_page
            # yield Request(weibo_list_url, callback=self.parse_weibo_list, meta=response.meta,dont_filter=True)

    # 获取关注者的信息
    def parse_fllow(self, response):
        data = response.text
        content = json.loads(data).get('data')
        cards = content.get('cards')
        if len(cards) > 0:
            # 获取关注人的信息
            for card in cards:
                for tmp in card.get('card_group'):
                    # 获取关注的人的ID
                    if tmp['card_type'] == 10:
                        user = tmp.get('user')
                        uid = user.get('id')
                        yield Request('https://m.weibo.cn/api/container/getIndex?type=uid&value=' + str(uid), callback=self.parse, dont_filter=True,
                                      meta={'uid': str(uid)})
            # 爬取下一页关注的人
            next_follow_page = str(int(response.meta['follow_page']) + 1)
            next_url = response.meta['base_url'] + next_follow_page
            # print('next_url:', next_url)
            yield Request(url=next_url, callback=self.parse_fllow, meta={'follow_page': next_follow_page, 'base_url': response.meta['base_url']},
                          dont_filter=True)

    # 日期格式化
    def date_format(self, datestr):
        now = datetime.datetime.now()
        ymd = now.strftime("%Y-%m-%d")
        y = now.strftime("%Y")
        newstr = datestr
        # 以下为手机端
        if datestr[4] == "-":
            newdate = datestr
        elif "-" in newstr:
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
# https://m.weibo.cn/p/index?containerid=231051_-_followers_-_1195354434_-_1042015%3AtagCategory_050&luicode=10000011&lfid=1076031195354434

# https://m.weibo.cn/api/container/getIndex?containerid=231051_-_followers_-_1195354434_-_1042015%3AtagCategory_050&luicode=10000011&lfid=1076031195354434
# https://m.weibo.cn/api/container/getIndex?containerid=231051_-_followers_-_1195354434_-_1042015:tagCategory_050&luicode=10000011&lfid=1076031195354434
# https://m.weibo.cn/api/container/getIndex?containerid=231051_-_followers_-_1195354434_-_1042015:tagCategory_050&luicode=10000011&lfid=1076031195354434&page=2
# https://m.weibo.cn/p/index?containerid=231051_-_followers_-_1195354434_-_1042015%3AtagCategory_050&luicode=10000011&lfid=1076031195354434

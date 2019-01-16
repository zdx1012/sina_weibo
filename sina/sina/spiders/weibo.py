# -*- coding: utf-8 -*-
import json

import scrapy
import datetime
import time
from scrapy import Request
from lxml import etree
from sina.items import personInfo, SinaItem


class WeiboSpider(scrapy.Spider):
    name = 'weibo'
    allowed_domains = ['m.weibo.cn']
    find_more_user = True  # 是否爬取其他的用户信息以及微博

    def start_requests(self):
        weibo_id = [2656274875, 5187664653, 1223178222, 1291477752, 1784473157, 1227368500]
        for wid in weibo_id:
            # print('https://m.weibo.cn/api/container/getIndex?type=uid&value=' + str(wid))
            yield Request('https://m.weibo.cn/api/container/getIndex?type=uid&value=' + str(wid), callback=self.parse_userInfo, dont_filter=True,
                          meta={'uid': str(wid)})
            print('this is a test ')

    # 解析个人信息
    def parse_userInfo(self, response):
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
            uid = response.meta['uid']
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
            yield Request('https://m.weibo.cn/api/container/getIndex?type=uid&value=' + uid, callback=self.parse_containerid, meta=response.meta,
                          dont_filter=False)

    # 解析containerid(获取微博需要该字段)
    def parse_containerid(self, response):
        uid = response.meta['uid']
        data = response.text
        content = json.loads(data).get('data')
        for data in content.get('tabsInfo').get('tabs'):
            if (data.get('tab_type') == 'weibo'):
                containerid = data.get('containerid')
                weibo_list_url = 'https://m.weibo.cn/api/container/getIndex?type=uid&value=' + uid + '&containerid=' + containerid + '&page=1'
                yield Request(weibo_list_url, callback=self.parse_weibo_list, meta={'page': 1, 'containerid': containerid, 'uid': uid})

    # 解析微博列表
    def parse_weibo_list(self, response):
        # 取相关信息，方便爬取下一页
        next_page = str(int(response.meta['page']) + 1)
        uid = response.meta['uid']
        containerid = response.meta['containerid']

        data = response.text
        content = json.loads(data).get('data')
        cards = content.get('cards')

        if (len(cards) > 0):
            # print("-----正在爬取第%s页-----" % str(response.meta['page']))
            tmp_time = ""
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
                    yield Request(url=fllow_base_url + str(1), callback=self.parse_fllow, meta={'page': 1, 'base_url': fllow_base_url})
            # 下一页链接
            # weibo_list_url = 'https://m.weibo.cn/api/container/getIndex?type=uid&value=' + uid + '&containerid=' + containerid + '&page=' + next_page
            # response.meta['page'] = next_page
            # yield Request(weibo_list_url, callback=self.parse_weibo_list, meta=response.meta)

    # 获取关注者的信息
    def parse_fllow(self, response):
        data = response.text
        content = json.loads(data).get('data')
        cards = content.get('cards')
        if len(cards) > 0:
            for card in cards:
                for tmp in card.get('card_group'):
                    # 获取关注的人的ID
                    if tmp['card_type'] == 10:
                        user = tmp.get('user')
                        uid = user.get('id')
                        yield Request('https://m.weibo.cn/api/container/getIndex?type=uid&value=' + str(uid), callback=self.parse_userInfo, dont_filter=False,
                                      meta={'uid': str(uid)})
            # 爬取下一页关注的微博主
            next_page = str(int(response.meta['page']) + 1)
            next_url = response.meta['base_url'] + next_page
            yield Request(url=next_url, callback=self.parse_fllow, meta={'page': next_page, 'base_url': response.meta['base_url']}, dont_filter=False)

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

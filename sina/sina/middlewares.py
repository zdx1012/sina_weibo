# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html
import logging
import random
import time

import redis
from scrapy import signals
from scrapy.downloadermiddlewares.retry import RetryMiddleware
from scrapy.utils.response import response_status_message


class SinaSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class SinaDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


redis_obj = redis.Redis(host='127.0.0.1', port=6379, db=0, decode_responses=True)


def get_proxy():
    # return redis_obj.srandmember('ip_set', 1)[0]
    return random.choice(redis_obj.hkeys(name="useful_proxy"))


def delete_proxy(cur_proxy):
    # redis_obj.srem('ip_set', str(cur_proxy).replace('http://', ''))
    redis_obj.hdel("useful_proxy", cur_proxy)


class RandomProxy(object):

    def process_request(self, request, spider):
        ip = get_proxy()
        if ip:
            request.meta['proxy'] = "http://" + ip

    def process_response(self, request, response, spider):
        # 处理非正常的http返回码
        cur_proxy = request.meta['proxy']
        # 如果状态码大于400，我们认为可能是被对方封掉了
        if response.status >= 400:
            with open('a.txt', encoding='utf-8', mode='a') as f:
                import datetime
                f.write(str(datetime.datetime.now()) + "---" + response.url + "---" + str(cur_proxy))
            # 删除IP代理
            delete_proxy(cur_proxy)
            # 将IP从当前的request对象中删除
            del request.meta['proxy']
            # 重新新安排该request调度下载
            return request
        return response

    def process_exception(self, request, exception, spider):
        #  处理请求过程中发和异常的情况
        # 通常是代理服务器本身挂掉了，或者网络原因
        if "proxy" in dict(request.meta).keys():
            cur_proxy = request.meta['proxy']
            print('raise exption: %s when use %s' % (exception, cur_proxy))
            # 删除IP代理
            # redis_obj.srem('ip_set', str(cur_proxy).replace('http://', ''))
            delete_proxy(cur_proxy)
            # 将IP从当前的request对象中删除
            del request.meta['proxy']
        # 从新安排该request调度下载
        return request

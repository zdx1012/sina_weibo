#!/usr/bin/env python
# -*- coding: utf-8 -*-

if __name__ == '__main__':
    import redis

    redis_obj = redis.Redis(decode_responses=True)
    redis_obj.lpush('WeiboSpider:start_urls', 'https://m.weibo.cn/api/container/getIndex?type=uid&value=1686532492')
    redis_obj.lpush('WeiboSpider:start_urls', 'https://m.weibo.cn/api/container/getIndex?type=uid&value=5611549371')
    redis_obj.lpush('WeiboSpider:start_urls', 'https://m.weibo.cn/api/container/getIndex?type=uid&value=2377156730')
    redis_obj.lpush('WeiboSpider:start_urls', 'https://m.weibo.cn/api/container/getIndex?type=uid&value=1246850033')

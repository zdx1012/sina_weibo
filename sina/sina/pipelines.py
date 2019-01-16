# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymysql
import json

MYSQL_HOST = 'localhost'
MYSQL_PORT = 3306
MYSQL_USER = 'root'
MYSQL_PWD = 'root'
MYSQL_DB = 'weibo'


class SinaPipeline(object):
    def process_item(self, item, spider):
        conn = pymysql.connect(host=MYSQL_HOST, port=MYSQL_PORT, db=MYSQL_DB, user=MYSQL_USER, passwd=MYSQL_PWD, charset='utf8')
        cursor = conn.cursor()
        # 根据是否有name字段，来判断是'用户信息'还是'微博'
        if 'name' in item.keys():
            sql = "REPLACE INTO sina_user(uid, name, profile_image_url, followers_count, follow_count, profile_url, description, verified, gender, urank,verified_type,verified_reason) values ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')" % (
                item['uid'], pymysql.escape_string(item['name']), item['profile_image_url'], item['followers_count'], item['follow_count'], item['profile_url'],
                pymysql.escape_string(item['description']), item['verified'], item['gender'], item['urank'], item['verified_type'], pymysql.escape_string(item['verified_reason']))
        else:
            sql = "INSERT INTO sina_weibo( uid, text, scheme, created_at, attitudes_count, comments_count, pictures) VALUES ('%s','%s','%s','%s','%s','%s','%s');" % (
                item['uid'], pymysql.escape_string(item['text']), item['scheme'], item['created_at'], item['attitudes_count'], item['comments_count'],
                json.dumps(item['pictures']),
            )
        try:
            cursor.execute(sql)
        except BaseException as e:
            print(e.args)
            print(sql)
        conn.commit()
        cursor.close()
        conn.close()
        return item

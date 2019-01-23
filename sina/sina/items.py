# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class personInfo(scrapy.Item):
    uid = scrapy.Field()  # 用户ID
    name = scrapy.Field()  # 昵称
    profile_url = scrapy.Field()  # 头像
    followers_count = scrapy.Field()  # 粉丝数
    follow_count = scrapy.Field()  # 关注数
    profile_image_url = scrapy.Field()  # 微博主页地址
    description = scrapy.Field()  # 描述
    verified = scrapy.Field()  # 是否认证
    gender = scrapy.Field()  # 性别
    urank = scrapy.Field()  # 等级
    verified_type = scrapy.Field()  # 认证类型
    verified_reason = scrapy.Field()  # 认证原因


class SinaItem(scrapy.Item):
    uid = scrapy.Field()
    text = scrapy.Field()
    scheme = scrapy.Field()
    created_at = scrapy.Field()
    attitudes_count = scrapy.Field()
    comments_count = scrapy.Field()
    pictures = scrapy.Field()
    reposts_count = scrapy.Field()


"""

CREATE TABLE `sina_user`  (
  `uid` int(11) NOT NULL,
  `name` varchar(255) CHARACTER SET utf8 COLLATE utf8_bin DEFAULT NULL,
  `profile_image_url` varchar(255) CHARACTER SET utf8 COLLATE utf8_bin DEFAULT NULL,
  `followers_count` int(11) DEFAULT NULL,
  `follow_count` int(11) DEFAULT NULL,
  `profile_url` varchar(255) CHARACTER SET utf8 COLLATE utf8_bin DEFAULT NULL,
  `description` text(0) CHARACTER SET utf8 COLLATE utf8_bin DEFAULT NULL,
  `verified` varchar(255) DEFAULT NULL,
  `gender` varchar(255) CHARACTER SET utf8 COLLATE utf8_bin DEFAULT NULL,
  `urank` varchar(255) CHARACTER SET utf8 COLLATE utf8_bin DEFAULT NULL,
  `verified_type` varchar(255) CHARACTER SET utf8 COLLATE utf8_bin DEFAULT NULL COMMENT '认证类别',
  `verified_reason` varchar(255) CHARACTER SET utf8 COLLATE utf8_bin DEFAULT NULL,
  PRIMARY KEY (`uid`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8 COLLATE = utf8_bin ROW_FORMAT = Compact;


CREATE TABLE `sina_weibo`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `uid` int(11) NOT NULL,
  `text` varchar(255) CHARACTER SET utf8 COLLATE utf8_bin DEFAULT NULL COMMENT '内容',
  `scheme` varchar(255) CHARACTER SET utf8 COLLATE utf8_bin DEFAULT NULL COMMENT '微博详情页',
  `created_at` date DEFAULT NULL COMMENT '日期',
  `attitudes_count` int(11) DEFAULT NULL COMMENT '点赞',
  `comments_count` int(11) DEFAULT NULL COMMENT '评论',
  `pictures` text CHARACTER SET utf8 COLLATE utf8_bin COMMENT '正文配图',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8 COLLATE = utf8_bin ROW_FORMAT = Compact;

"""

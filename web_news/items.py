# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field
from scrapy.loader.processors import Join, Compose


class SpiderItem(Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    url = Field(output_processor=Join(separator=''))
    date = Field(output_processor=Join(separator=''))
    source = Field(output_processor=Join(separator=''))
    title = Field(output_processor=Join(separator=''))
    abstract = Field(output_processor=Join(separator=''))
    content = Field(output_processor=Join(separator=''))
    md5 = Field(output_processor=Join(separator=''))
    collection_name = Field(output_processor=Join(separator=''))
    view_num = Field(output_processor=Join(separator=''))
    brief = Field(output_processor=Join(separator=''))
    website = Field(output_processor=Join(separator=''))


class WeiboItem(Item):
    url = Field(output_processor=Join(separator=''))
    user = Field(output_processor=Join(separator=''))
    date = Field(output_processor=Join(separator=''))
    content = Field(output_processor=Join(separator=''))
    md5 = Field(output_processor=Join(separator=''))
    reposts_count = Field(output_processor=Join(separator=''))
    comments_count = Field(output_processor=Join(separator=''))
    attitudes_count = Field(output_processor=Join(separator=''))
    collection_name = Field(output_processor=Join(separator=''))
    website = Field(output_processor=Join(separator=''))


class ZhihuAnswerItem(Item):
    url = Field(output_processor=Join(separator=''))
    date = Field(output_processor=Join(separator=''))
    answer_id = Field(output_processor=Join(separator=''))
    user_url = Field(output_processor=Join(separator=''))
    question_id = Field(output_processor=Join(separator=''))
    question_url = Field(output_processor=Join(separator=''))
    agree_num = Field(output_processor=Join(separator=''))
    summary = Field(output_processor=Join(separator=''))
    content = Field(output_processor=Join(separator=''))
    md5 = Field(output_processor=Join(separator=''))
    comment_num = Field(output_processor=Join(separator=''))
    collection_name = Field(output_processor=Join(separator=''))
    website = Field(output_processor=Join(separator=''))


class DoubanCommentItem(Item):
    url = Field(output_processor=Join(separator=''))
    sentiment = Field(output_processor=Join(separator=''))
    level = Field(output_processor=Join(separator=''))
    content = Field(output_processor=Join(separator=''))
    md5 = Field(output_processor=Join(separator=''))
    collection_name = Field(output_processor=Join(separator=''))
    website = Field(output_processor=Join(separator=''))


class FroumItem(Item):
    url = Field(output_processor=Join(separator=''))
    date = Field(output_processor=Join(separator=''))
    last_reply = Field(output_processor=Join(separator=''))
    title = Field(output_processor=Join(separator=''))
    content = Field(output_processor=Join(separator=''))
    md5 = Field(output_processor=Join(separator=''))
    collection_name = Field(output_processor=Join(separator=''))
    view_num = Field(output_processor=Join(separator=''))
    reply_num = Field(output_processor=Join(separator=''))
    website = Field(output_processor=Join(separator=''))
    key = Field(output_processor=Join(separator=''))


class FroumReplyItem(Item):
    url = Field(output_processor=Join(separator=''))
    date = Field(output_processor=Join(separator=''))
    content = Field(output_processor=Join(separator=''))
    md5 = Field(output_processor=Join(separator=''))
    collection_name = Field(output_processor=Join(separator=''))
    website = Field(output_processor=Join(separator=''))
    replyid = Field(output_processor=Join(separator=''))
    key = Field(output_processor=Join(separator=''))

# -*- coding:utf-8 -*-
from scrapy.spiders import Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader
from ..misc.spiderredis import SpiderRedis
from ..items import DoubanCommentItem


class Douban(SpiderRedis):
    name = "douban"
    website = "豆瓣网"
    allowed_domains = ["movie.douban.com"]
    start_urls = ['https://movie.douban.com/subject/25900945/comments?status=P']

    rules = [
        Rule(LinkExtractor("subject/25900945/comments.*?status=P"), callback="get_comments", follow=True)
    ]

    sentiment_map = {u'力荐': '5', u'推荐': '4', u'还行': '3', u'较差': '2', u'很差': '1'}

    def get_comments(self, response):
        comments = response.xpath('//div[@class="comment-item"]')
        for comment in comments:
            loader = ItemLoader(item=DoubanCommentItem(), response=response)
            try:
                sentiment = comment.xpath('div[@class="comment"]/h3/span[2]/span[2]/@title').extract_first()
                loader.add_value("sentiment", sentiment)
                loader.add_value("content",
                                 ''.join(comment.xpath('div[@class="comment"]/p/text()').extract()))
                loader.add_value("level", self.sentiment_map.get(sentiment, ''))
            except Exception as e:
                self.logger.error('error url: %s error msg: %s' % (response.url, e))
                loader.add_value('sentiment', '')
                loader.add_value("level", '')
                loader.add_value('content', '')

            loader.add_value('url', comment.xpath('@data-cid').extract_first())
            loader.add_value('collection_name', self.name)
            loader.add_value('website', self.website)

            return loader.load_item()

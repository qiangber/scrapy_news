# -*- coding: utf-8 -*-
from scrapy.spiders import Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader
from web_news.items import SpiderItem
from web_news.misc.spiderredis import SpiderRedis


class Ynet(SpiderRedis):
    name = "ynet"
    website = "北青网"
    allowed_domain = "ynet.com"
    start_urls = ['http://www.ynet.com/']

    rules = [
        Rule(LinkExtractor(allow=("\d{4}/\d{2}/\d{8}.html$",), deny=("ly", "ent")), callback="get_news", follow=False),
        Rule(LinkExtractor("news", "society", "finance", "life", "report"), follow=True)
    ]

    def get_news(self, response):
        loader = ItemLoader(item=SpiderItem(), response=response)
        try:
            loader.add_value("title", response.xpath('//div[@class="articleTitle"]/h2/text()').extract_first())
            loader.add_value("title", response.xpath('//h1[@class=" BSHARE_POP"]/text()').extract_first())

            loader.add_value("date", response.xpath('//span[@class="yearMsg"]/text()').extract_first())
            loader.add_value("date", response.xpath('//span[@id="pubtime_baidu"]/text()').extract_first())

            loader.add_value("source", response.xpath('//span[@class="sourceMsg"]/text()').extract_first())

            loader.add_value("content", ''.join(
                response.xpath('//div[@class="articleBox mb20 cfix"]/descendant-or-self::text()').extract()))
            loader.add_value("content", ''.join(
                response.xpath('//div[@id="pzoom"]/p/descendant::text()').extract()))
        except Exception as e:
            self.logger.error('error url: %s error msg: %s' % (response.url, e))
            loader.add_value('title', '')
            loader.add_value("source", '')
            loader.add_value('date', '1970-01-01 00:00:00')
            loader.add_value('content', '')

        loader.add_value('url', response.url)
        loader.add_value('collection_name', self.name)
        loader.add_value('website', self.website)

        yield loader.load_item()

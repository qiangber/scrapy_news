# -*- coding:utf-8 -*-
from scrapy.spiders import Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader
from web_news.items import SpiderItem
from web_news.misc.spiderredis import SpiderRedis


class Gmw(SpiderRedis):
    name = "gmw"
    website = "光明网"
    allowed_domains = ["gmw.cn"]
    start_urls = ['http://www.gmw.cn/']

    rules = [
        Rule(LinkExtractor("(news|politics|world|difang|guancha|theory|dangjian|culture|tech|edu|economy"
                           "|life|mil|legal|finance).*?content_"), callback="get_news", follow=False),
        Rule(LinkExtractor("(news|politics|world|difang|guancha|theory|dangjian|culture|tech|edu|economy"
                           "|life|mil|legal|finance).*?node_"), follow=True)
    ]

    def get_news(self, response):
        loader = ItemLoader(item=SpiderItem(), response=response)
        try:
            loader.add_value("title", response.xpath('//h1[@id="articleTitle"]/text()').extract_first())
            loader.add_value("title", response.xpath('//div[@id="articleTitle"]/text()').extract_first())
            loader.add_value("title", response.xpath('//h2[@id="toptitle"]/a/text()').extract_first())
            loader.add_value("title", response.xpath('//div[@class="tit_dt"]/b/text()').extract_first())
            loader.add_value("title", response.xpath('//div[@id="ArticleTitle"]/text()').extract_first())
            loader.add_value("title", response.xpath('//h1[@class="picContentHeading"]/text()').extract_first())

            date = response.xpath('//span[@id="pubTime"]/text()').extract_first()
            if date:
                loader.add_value("date", date + ":00")
            loader.add_value("date",
                             ''.join(response.xpath('//div[@id="ArticleSourceAuthor"]/text()').extract()).strip()[:19])
            if loader.get_collected_values("date") == '':
                end = response.url.find('/content_')
                loader.add_value("date", response.url[end-10:end].replace('/', '-') + " 00:00:00")

            loader.add_value("content",
                             ''.join(response.xpath('//div[@id="contentMain"]/descendant-or-self::text()').extract()))
            loader.add_value("content", ''.join(response.xpath(
                '//div[@style="padding:15px 15px;line-height:28px;"]/descendant-or-self::text()').extract()))
            loader.add_value("content", ''.join(response.xpath('//div[@class="con_dt"]/descendant::text()').extract()))
            loader.add_value("content",
                             ''.join(response.xpath('//div[@id="ArticleContent"]/descendant::text()').extract()))

        except Exception as e:
            self.logger.error('error url: %s error msg: %s' % (response.url, e))
            loader.add_value('title', '')
            loader.add_value('date', '1970-01-01 00:00:00')
            loader.add_value('content', '')

        loader.add_value('url', response.url)
        loader.add_value('collection_name', self.name)
        loader.add_value('website', self.website)

        return loader.load_item()

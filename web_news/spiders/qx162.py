# -*- coding: utf-8 -*-
from scrapy.spiders import Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.http import Request, HtmlResponse
from scrapy.loader import ItemLoader
from web_news.misc.filter import Filter
from web_news.items import *
from web_news.misc.spiderredis import SpiderRedis


class Qx162(SpiderRedis):
    name = "qx162"
    website = "黔讯网"
    allowed_domains = ['qx162.com']
    start_urls = ['http://qx162.com/']

    rules = [
        Rule(LinkExtractor(allow=("/\d+?\.shtml",)), callback="get_news", follow=True),
        Rule(LinkExtractor(allow=("news\.qx162\.com", "house\.qx162\.com", "tech\.qx162\.com")), follow=True),
    ]

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(Qx162, cls).from_crawler(crawler, *args, **kwargs)
        spider.filter = Filter.from_crawler(spider.crawler, spider.name)
        return spider

    def _requests_to_follow(self, response):
        links = self.filter.bool_fllow(response, self.rules)
        if len(links) > 0:
            for link in links:
                r = Request(url=link.url, callback=self._response_downloaded)
                r.meta.update(rule=0, link_text=link.text)
                yield self.rules[0].process_request(r)
            if not isinstance(response, HtmlResponse):
                return
            seen = set()
            for n, rule in enumerate(self._rules):
                if n == 0:
                    continue
                links = [lnk for lnk in rule.link_extractor.extract_links(response)
                         if lnk not in seen]
                if links and rule.process_links:
                    links = rule.process_links(links)
                for link in links:
                    seen.add(link)
                    r = Request(url=link.url, callback=self._response_downloaded)
                    r.meta.update(rule=n, link_text=link.text)
                    yield rule.process_request(r)
        else:
            return

    def get_news(self, response):
        try:
            loader = ItemLoader(item=SpiderItem(), response=response)

            loader.add_value('title', response.xpath('//div[@class="left"]/h1/text()').extract_first())
            loader.add_value('title', response.xpath('//h1[@class="h1"]/text()').extract_first())

            loader.add_value('date', response.xpath('//div[@class="zuoze"]/text()').extract_first())
            loader.add_value('date', response.xpath('//span[@class="post-time"]/text()').extract_first())
            date = ''.join(loader.get_collected_values('date'))
            if date == '':
                return
            loader.replace_value('date', date.strip() + ":00")

            loader.add_value('content',
                             ''.join(response.xpath('//span[@id="zoom"]/descendant-or-self::text()').extract()))
            loader.add_value('content',
                             ''.join(response.xpath('//p[@class="summary"]/descendant-or-self::text()').extract()))

            loader.add_value('url', response.url)
            loader.add_value('collection_name', self.name)
            loader.add_value('website', self.website)

            yield loader.load_item()
        except Exception as e:
            self.logger.error('error url: %s error msg: %s' % (response.url, e))
            l = ItemLoader(item=SpiderItem(), response=response)
            l.add_value('title', '')
            l.add_value('date', '1970-01-01 00:00:00')
            l.add_value('source', '')
            l.add_value('content', '')
            l.add_value('url', response.url)
            l.add_value('collection_name', self.name)
            l.add_value('website', self.website)
            yield l.load_item()
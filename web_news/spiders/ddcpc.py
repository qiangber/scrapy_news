# -*- coding: utf-8 -*-
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.http import Request, HtmlResponse
from scrapy.loader import ItemLoader
from web_news.misc.filter import Filter
from web_news.items import *


class Ddcpc(CrawlSpider):
    name = "ddcpc"
    website = "当代先锋网"
    allowed_domains = ['ddcpc.cn']
    start_urls = ['http://www.ddcpc.cn/']

    rules = [
        Rule(LinkExtractor(allow=("jr_", "gz_", "rs_", "xf_", "xcb_",
                                  "a=show&catid=(561|562|563|564|565|567|569|572|)")),
             callback="get_news", follow=False),
        Rule(LinkExtractor(allow=("/zx/", "/dj/", "/zx/rs/" "/pl/xf/", "/zx/xcb/",
                                  "a=lists&catid=(561|562|563|564|565|567|569|572|)")),
             follow=True),
    ]

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(Ddcpc, cls).from_crawler(crawler, *args, **kwargs)
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

            loader.add_value('title', response.xpath('//div[@class="title"]/h2/text()').extract_first())

            date = ''.join(response.xpath('//div[@class="auther-from"]/text()').extract())
            loader.add_value('date', date[-19:])

            loader.add_value('content',
                             ''.join(response.xpath('//div[@class="content"]/descendant-or-self::text()').extract()))

            loader.add_value('url', response.url)
            loader.add_value('collection_name', self.name)
            loader.add_value('website', self.website)

            return loader.load_item()
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
            return l.load_item()
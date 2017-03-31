# -*- coding: utf-8 -*-
import json

from scrapy import signals
from scrapy.exceptions import DontCloseSpider
from scrapy.spiders import CrawlSpider, Spider
from scrapy.http import Request, HtmlResponse

from web_news.misc.LogSpider import LogStatsDIY
from web_news.misc.filter import Filter


class IncrementCrawlSpider(Spider):

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(IncrementCrawlSpider, cls).from_crawler(crawler, *args, **kwargs)
        spider.filter = Filter.from_crawler(spider.crawler, spider.name)
        spider.crawler.signals.connect(spider.spider_idle, signal=signals.spider_idle)
        spider.l = LogStatsDIY.from_crawler(crawler)
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

    def spider_idle(self):
        """Schedules a request if available, otherwise waits."""
        # XXX: Handle a sentinel to close the spider.
        # sleep somtime ?
        self.logger.info('restart')
        # start_requests won't be filtered
        for req in self.start_requests():
            self.crawler.engine.crawl(req, spider=self)
        raise DontCloseSpider
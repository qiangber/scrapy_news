from scrapy.spiders import Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader
from web_news.misc.increment_crawl_spider import IncrementCrawlSpider
from web_news.items import SpiderItem
import time


class Weiyuanhui(IncrementCrawlSpider):
    name = "mitbbs"
    website = "未名论坛"
    allowed_domain = "mitbbs.com"
    start_urls = ['http://www.mitbbs.com/']

    rules = [
        Rule(LinkExtractor(allow=("article_t",)), callback="get_news", follow=True),
        Rule(LinkExtractor(allow=("bbsdoc",)), follow=True)
    ]

    def get_news(self, response):
        loader = ItemLoader(item=SpiderItem(), response=response)
        try:
            loader.add_value("title",
                             response.xpath('//span[@class="jiatype16"]/strong[1]/text()').extract_first())

            date = time.strptime(response.xpath('//td[@class="news-bg"]/table//tr[2]/td/text()').extract()[-1][-19:],
                                 "%Y年%m月%d日%H:%M:%S")
            loader.add_value("date", time.strftime("%Y-%m-%d %H:%M:%S", date))

            loader.add_value("content", ''.join(
                response.xpath('//td[@class="jiawenzhang-type"]/descendant-or-self::text()').extract()))
        except Exception as e:
            self.logger.error('error url: %s error msg: %s' % (response.url, e))
            loader.add_value('title', '')
            loader.add_value('date', '1970-01-01 00:00:00')
            loader.add_value('content', '')

        loader.add_value('url', response.url)
        loader.add_value('collection_name', self.name)
        loader.add_value('website', self.website)

        return loader.load_item()

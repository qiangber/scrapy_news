from scrapy.spiders import Spider
from scrapy.http import Request
from scrapy.loader import ItemLoader
import time
import json
from web_news.items import *


class Toutiao(Spider):
    name = "toutiao"
    website = "今日头条"
    allowed_domains = ['toutiao.com']
    custom_settings = {
        "DOWNLOAD_DELAY": 1,
    }

    def start_requests(self):
        get_url = "http://toutiao.com/api/article/feed/?utm_source=toutiao&as=A11548E038C8FC9&cp=5808182F8CC9AE1"
        categorys = ["news_society", "news_tech", "news_military", "news_world", "news_finance"]
        for category in categorys:
            timestamp = int(time.mktime(time.localtime()))
            yield Request(url=get_url + '&category=' + category + '&_=' + str(timestamp), callback=self.parse)

    def parse(self, response):
        data = json.loads(response.body_as_unicode())
        next_page = data['next']['max_behot_time']
        category = data['data'][0]['tag']
        for data in data['data']:
            if data['article_genre'] == 'article':
                yield Request(
                    url="http://www.toutiao.com" + data['source_url'].replace('group/', 'a'), callback=self.parse_item)
        get_url = "http://toutiao.com/api/article/feed/?utm_source=toutiao&as=A11548E038C8FC9&cp=5808182F8CC9AE1"
        yield Request(url=get_url + '&category=' + category + '&max_behot_time=' + str(next_page), callback=self.parse)

    def parse_item(self, response):
        if response.url.find('toutiao.com') > 0 and response.url.find('?_as_') == -1:
            loader = ItemLoader(item=SpiderItem(), response=response)

            loader.add_value('title', response.xpath('//h1[@class="title"]/text()').extract())
            loader.add_value('title', response.xpath('//h1[@class="article-title"]/text()').extract())

            loader.add_value('date', response.xpath('//span[@class="time"]/text()').extract_first() + ":00")

            loader.add_value('content', ''.join(
                response.xpath('//div[@class="article-content"]/descendant-or-self::text()').extract()))

            loader.add_value('url', response.url)
            loader.add_value('collection_name', self.name)
            loader.add_value('website', self.website)

            yield loader.load_item()
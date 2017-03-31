# -*- coding: utf-8 -*-
from scrapy import Selector
from selenium import webdriver
from web_news.items import WeiboItem
import time
from web_news.misc.pureSpiderredis import PureSpiderRedis


class renming_weibo(PureSpiderRedis):
    name = "renming_weibo2"
    website = "人民微博"
    start_urls = ["http://t.people.com.cn/538925"]
    allowed_domains = ["people.com.cn"]

    def parse(self, response):
        browser = webdriver.Firefox()
        browser.get(response.url)
        selector = Selector(text=browser.page_source)
        div_results = selector.xpath('//div[@class="list_detail"]')
        for result in div_results:
            try:
                item = WeiboItem()
                item['username'] = result.xpath('div[@class="list_user"]/a[1]/@data-nickname').extract_first()
                item['url'] = 'http://t.people.com.cn' + result.xpath('div[@class="list_bottom skin_color_02 clearfix"]/div[@class="list_time"]/a[1]/@href').extract_first()
                time_stamp = result.xpath('div[@class="list_bottom skin_color_02 clearfix"]/div[@class="list_time"]/a[1]/@data-posttime').extract_first()
                item['date'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(float(time_stamp)))
                item['content'] = result.xpath('div[@class="list_text skin_color_01"]/text()').extract_first()
                attitudes_count = result.xpath('div[@class="list_bottom skin_color_02 clearfix"]/div[@class="list_func"]/a[@data-nodetype="btn_agree"]/span/text()').extract_first()
                item['attitudes_count'] = 0 if attitudes_count is None else attitudes_count[1:-1]
                comments_count = result.xpath('div[@class="list_bottom skin_color_02 clearfix"]/div[@class="list_func"]/a[@data-nodetype="btn_forward"]/text()').extract_first()
                item['comments_count'] = 0 if comments_count is None else comments_count[3:-1]
                reposts_count = result.xpath('div[@class="list_bottom skin_color_02 clearfix"]/div[@class="list_func"]/a[@data-nodetype="btn_comment"]/text()').extract_first()
                item['reposts_count'] = 0 if reposts_count is None else reposts_count[3:-1]
            except Exception as e:
                self.logger.error('error url: %s error msg: %s' % (response.url, e))
                item['date'] = '1970-01-01 00:00:00'
                item['content'] = ''
            item['collection_name'] = self.name
            item['website'] = self.website
            yield item
        browser.close()
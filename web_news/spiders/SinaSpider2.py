# -*- coding:utf-8 -*-
from scrapy.spiders import Spider
from scrapy.http import Request
import json
from web_news.items import SpiderItem
from web_news.misc.pureSpiderredis import PureSpiderRedis


class SinaSpider(PureSpiderRedis):
    name = "weibo_news"
    website = "新浪微博"
    allowed_domains = ["weibo.cn"]
    count = 0

    def start_requests(self):
        url = "http://m.weibo.cn/page/json?containerid=1005052803301701_-_WEIBO_SECOND_PROFILE_WEIBO&page=181"
        headers = {
            'Host': "m.weibo.cn",
            'Referer': "http://m.weibo.cn/page/tpl?containerid=1005052803301701_-_WEIBO_SECOND_PROFILE_WEIBO&"
                       "itemid=&title=%E5%85%A8%E9%83%A8%E5%BE%AE%E5%8D%9A"
        }
        yield Request(url=url, callback=self.parse, headers=headers)

    def parse(self, response):
        try:
            msg = json.loads(response.body_as_unicode())
            for data in msg['cards'][0]['card_group']:
                item = SpiderItem()
                item["content"] = data['mblog']['text']
                item["url"] = "http://m.weibo.cn/" + str(data['mblog']['user']['id']) + '/' + data['mblog']['bid']
                item["collection_name"] = self.name
                item["website"] = self.website
                count = msg['count']
                yield item
        except Exception as e:
            self.logger.error('error url: %s error msg: %s' % (response.url, e))
        finally:
            url = response.url
            page = int(url[url.find('page=')+5:])
            if page * 10 < count:
                url = "http://m.weibo.cn/page/json?containerid=1005052803301701_-_WEIBO_SECOND_PROFILE_WEIBO&page="\
                      + str(page + 1)
                headers = {
                    'Host': "m.weibo.cn",
                    'Referer': "http://m.weibo.cn/page/tpl?containerid=1005052803301701_-_WEIBO_SECOND_PROFILE_WEIBO&"
                               "itemid=&title=%E5%85%A8%E9%83%A8%E5%BE%AE%E5%8D%9A"
                }
                print(url)
                yield Request(url=url, callback=self.parse, headers=headers)
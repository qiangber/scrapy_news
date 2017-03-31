# -*- coding:utf-8 -*-
import time
from scrapy.spiders import Spider
from scrapy.http import Request
import json
from web_news.items import WeiboItem


class SinaSpider(Spider):
    name = "weibo_news"
    website = "新浪微博"
    allowed_domains = ["weibo.cn"]
    userids = ["5943888653", "2337828931", "2739500220"]
    count = 0

    def start_requests(self):
        for userid in self.userids:
            url = "http://m.weibo.cn/page/json?containerid=100505%s_-_WEIBO_SECOND_PROFILE_WEIBO&page=1" % userid
            headers = {
                'Host': "m.weibo.cn",
                'Referer': "http://m.weibo.cn/page/tpl?containerid=100505%s_-_WEIBO_SECOND_PROFILE_WEIBO&" % userid +
                           "itemid=&title=%E5%85%A8%E9%83%A8%E5%BE%AE%E5%8D%9A"
            }
            yield Request(url=url, callback=self.parse, headers=headers)

    def parse(self, response):
        try:
            msg = json.loads(response.body_as_unicode())
            count = int(msg['count'])
            for data in msg['cards'][0]['card_group']:
                userid = str(data['mblog']['user']['id'])
                item = WeiboItem()
                item["content"] = data['mblog']['text']
                item["url"] = "http://m.weibo.cn/" + userid + '/' + data['mblog']['bid']
                item["reposts_count"] = data["mblog"]["reposts_count"]
                item["comments_count"] = data["mblog"]["comments_count"]
                item["attitudes_count"] = data["mblog"]["attitudes_count"]
                item["date"] = time.strftime("%Y-%m-%d", time.localtime(data["mblog"]["created_timestamp"]))
                item["collection_name"] = self.name
                item["website"] = self.website
                yield item
        except Exception as e:
            self.logger.error('error url: %s error msg: %s' % (response.url, e))
        finally:
            url = response.url
            page = int(url[url.find('page=')+5:])
            if page * 10 < count:
                url = "http://m.weibo.cn/page/json?containerid=100505%s_-_WEIBO_SECOND_PROFILE_WEIBO&page=%s" \
                      % (userid, page + 1)
                headers = {
                    'Host': "m.weibo.cn",
                    'Referer': "http://m.weibo.cn/page/tpl?containerid=100505%s_-_WEIBO_SECOND_PROFILE_WEIBO&" % userid
                    + "itemid=&title=%E5%85%A8%E9%83%A8%E5%BE%AE%E5%8D%9A"
                }
                print(url)
                yield Request(url=url, callback=self.parse, headers=headers)
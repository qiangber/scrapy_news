# import os
from scrapy.spiders import Spider
from scrapy.http import FormRequest
from scrapy.selector import Selector
import json
import re
from web_news.items import *
from math import ceil
import requests
import time

# if not os.path.exists('images'):
#     os.mkdir("images")


class ZhihuTopicSpider(Spider):
    name = 'zhihu'
    website = u'知乎'
    allowed_domains = ['zhihu.com']
    start_urls = ['https://www.zhihu.com/topics']
    download_delay = 3
    custom_settings = {
        'download_delay': 3,
    }

    def parse(self, response):
        for sel in response.xpath('//li[@class="zm-topic-cat-item"]'):
            topic_id = sel.xpath('@data-id').extract()[0]
            print("topic_id", topic_id)

            post_url = 'https://www.zhihu.com/node/TopicsPlazzaListV2'
            params = json.dumps({
                'topic_id': topic_id,
                'offset': 0,
                'hash_id': ''
            })
            data = {
                'method': 'next',
                'params': params
            }
            headers = {
                'User-Agent': "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36",
                'Host': "www.zhihu.com",
                'Referer': response.url
            }
            yield FormRequest(url=post_url, formdata=data, headers=headers, callback=self.get_topic)

    def get_topic(self, response):
        msg = json.loads(response.body_as_unicode())['msg']
        pattern = re.compile('<a.*?href="/topic/(.*?)">.*?<strong>(.*?)</strong>', re.S)
        topics = re.findall(pattern, ''.join(msg))
        for topic in topics:
            url = 'https://www.zhihu.com/topic/%s/hot' % topic[0]
            headers = {
                'User-Agent': "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36",
                'Host': "www.zhihu.com",
                'Referer': "https://www.zhihu.com/topics"
            }
            get_msg = requests.get(url=url, headers=headers)
            sel = Selector(response=get_msg)
            data_score = sel.xpath('//div[@itemprop="question"]/@data-score')
            offset = ceil(float(data_score.extract()[0]))
            if offset > 3100:
                headers['Referer'] = url
                data = {
                    'start': '0',
                    'offset': str(offset)
                }
                yield FormRequest(url=url, formdata=data, headers=headers, callback=self.get_question_info)

    def get_question_info(self, response):
        msg = json.loads(response.body_as_unicode())['msg']
        if int(msg[0]) <= 0:
            return
        pattern = re.compile('<a.*?class="question_link".*?href="/question/(.*?)".*?>(.*?)</a>', re.S)
        results = re.findall(pattern, ''.join(msg[1]))
        sel = Selector(text=msg[1])
        divs = sel.xpath('//div[@class="feed-item feed-item-hook  folding"]/@data-score').extract()
        offset = float(divs[-1])
        headers = {
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36",
            'Host': "www.zhihu.com",
            'Referer': response.url
        }
        if offset > 3100:
            data = {
                'start': '0',
                'offset': str(offset)
            }
            yield FormRequest(url=response.url, formdata=data, headers=headers, callback=self.get_question_info)
        for result in results:
            print("question_id", result[0])
            url = 'https://www.zhihu.com/question/%s' % result[0]
            get_msg = requests.get(url=url, headers=headers)
            sel = Selector(response=get_msg)
            answer_num = sel.xpath('//h3[@id="zh-question-answer-num"]/@data-num').extract()
            if len(answer_num) == 0:
                answer_num = 0
            else:
                answer_num = answer_num[0]
            post_url = "http://www.zhihu.com/node/QuestionAnswerListV2"
            params = json.dumps({
                'url_token': result[0],
                'pagesize': 10,
                'offset': 0
            })
            data = {
                '_xsrf': '',
                'method': 'next',
                'params': params
            }
            headers = {
                'User-Agent': "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:34.0) Gecko/20100101 Firefox/34.0",
                'Host': "www.zhihu.com",
                'Referer': url
            }
            meta = {'answer_num': answer_num, 'offset': 10}
            yield FormRequest(url=post_url, formdata=data, headers=headers, meta=meta, callback=self.get_answer_info)

    def get_answer_info(self, response):
        question_id = response.url.split('/')[-1]
        offset = int(response.meta['offset'])
        answer_num = int(response.meta['answer_num'])
        page_size = 10
        if offset < answer_num and offset < 30:
            post_url = "http://www.zhihu.com/node/QuestionAnswerListV2"
            params = json.dumps({
                'url_token': question_id,
                'pagesize': page_size,
                'offset': offset
            })
            data = {
                '_xsrf': '',
                'method': 'next',
                'params': params
            }
            headers = {
                'User-Agent': "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:34.0) Gecko/20100101 Firefox/34.0",
                'Host': "www.zhihu.com",
                'Referer': response.url
            }
            offset += page_size
            meta = {'answer_num': answer_num, 'offset': offset}
            yield FormRequest(url=post_url, formdata=data, headers=headers, meta=meta, callback=self.get_answer_info)

        answer_list = json.loads(response.body_as_unicode())['msg']
        # 爬取图片
        # img_urls = re.findall('img .*?data-actualsrc="(.*?_b.*?)"', ''.join(answer_list))
        # for img_url in img_urls:
        #     try:
        #         file_name = basename(img_url)
        #         print(file_name)
        #         img_data = request.urlopen(img_url).read()
        #         print('read success')
        #         output = open('images/' + file_name, 'ab')
        #         output.write(img_data)
        #         output.close()
        #     except Exception as e:
        #         print('read fail', e)
        for answer in answer_list:
            sel = Selector(text=answer)
            message = sel.xpath('//div[@class="zm-item-rich-text expandable js-collapse-body"]/@data-entry-url')\
                .extract_first()
            data_entry_url = message.split('/')
            question_id = data_entry_url[2]
            answer_id = data_entry_url[4]
            content = ''.join(
                sel.xpath('//div[@class="zm-editable-content clearfix"]/descendant-or-self::text()').extract())
            agree_num = sel.xpath('//span[@class="count"]/text()').extract_first()
            author_url = sel.xpath('//a[@class="author-link"]/@href').extract_first()
            if author_url:
                user_url = 'https://www.zhihu.com' + author_url
            else:
                user_url = '匿名用户'
            summary = ''.join(
                sel.xpath('//div[@class="zh-summary summary clearfix"]/descendant-or-self::text()').extract())
            comment_num = sel.xpath('//a[@class="meta-item toggle-comment js-toggleCommentBox"]//text()').extract()[1]
            pos = comment_num.find(" ")
            comment_num = comment_num[:pos] if pos != -1 else 0
            sec = sel.xpath('//div[@class="zm-item-answer  zm-item-expanded"]/@data-created').extract_first()

            answer_item = ZhihuAnswerItem()
            answer_item['url'] = "https://www.zhihu.com/question/" + question_id + "/answer/" + answer_id
            answer_item['date'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(float(sec)))
            answer_item['content'] = content
            answer_item['agree_num'] = agree_num
            answer_item['question_id'] = question_id
            answer_item['question_url'] = "https://www.zhihu.com/question/" + question_id
            answer_item['answer_id'] = answer_id
            answer_item['user_url'] = user_url
            answer_item['summary'] = summary
            answer_item['comment_num'] = comment_num
            answer_item['collection_name'] = self.name
            answer_item['website'] = self.website

            yield answer_item
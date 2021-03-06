import logging
import time
import datetime
import json
from scrapy import signals
from twisted.internet import task

from web_news.pipelines import MongoDBPipeline

logger = logging.getLogger(__name__)

def date_handler(obj):
    if hasattr(obj, 'isoformat'):
        return obj.isoformat()
    else:
        raise TypeError

class LogStatsDIY(object):
    def __init__(self, stats, interval=60.0):
        self.stats = stats
        self.interval = interval
        self.multiplier = 60.0 / self.interval
        self.task = None

    @classmethod
    def from_crawler(cls, crawler):
        # o = super(LogStatsDIY, cls).from_crawler(crawler)
        o = cls(crawler.stats)
        o.mongo = MongoDBPipeline.from_crawler(crawler)
        o.db = o.mongo.db['LogStatsDIY']
        crawler.signals.connect(o.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(o.spider_closed, signal=signals.spider_closed)
        return o

    def spider_opened(self, spider):
        self.pagesprev = 0
        self.itemsprev = 0
        self.task = task.LoopingCall(self.log, spider)
        self.task.start(self.interval)

    def log(self, spider):
        items = self.stats.get_value('item_scraped_count', 0)
        pages = self.stats.get_value('response_received_count', 0)
        irate = (items - self.itemsprev) * self.multiplier
        prate = (pages - self.pagesprev) * self.multiplier
        self.pagesprev, self.itemsprev = pages, items

        log_args = {'pages': pages, 'pagerate': prate,
                    'items': items, 'itemrate': irate}
        item = {'name': spider.name}
        try:
            item['name'] += '-{}'.format(getattr(spider, 'key'))
        except Exception as e:
            pass
        item['active_date'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
        item.update(log_args)
        item['_stats'] = json.dumps(self.stats._stats, default=date_handler)
        logger.debug(item)
        # logger.info(msg, log_args, extra={'spider': spider})
        self.db.update({'name': item['name']}, {'$set': dict(item)}, True, True)
        
    def spider_closed(self, spider, reason):
        if self.task and self.task.running:
            self.task.stop()

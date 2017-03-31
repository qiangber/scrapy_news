from scrapy.commands import ScrapyCommand
from scrapy.utils.conf import arglist_to_dict
from scrapy.exceptions import UsageError
import time
import logging


class Command(ScrapyCommand):

    requires_project = True

    def syntax(self):
        return '[options]'

    def short_desc(self):
        return 'Runs all of the spiders'

    def process_options(self, args, opts):
        try:
            self.settings.setdict(arglist_to_dict(opts.set), priority='cmdline')
        except ValueError:
            raise UsageError("Invalid -s value, use -s NAME=VALUE", print_help=False)

    def run(self, args, opts):

        spider_loader = self.crawler_process.spider_loader

        for spider_name in spider_loader.list():
            logging.info("crawl %s in %s" % (spider_name, time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())))
            self.crawler_process.crawl(spider_name)

        self.crawler_process.start()
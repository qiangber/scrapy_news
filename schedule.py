__author__ = 'xuqiang'

import time
import os
import sched
import logging

schedule = sched.scheduler(time.time, time.sleep)

def perform_command(cmd, inc):
    # 安排inc秒后再次运行自己，即周期运行
    schedule.enter(inc, 0, perform_command, (cmd, inc))
    os.system(cmd)

def timming_exe(cmd, inc):
    # enter用来安排某事件的发生时间，从现在起第inc秒开始启动
    schedule.enter(0, 0, perform_command, (cmd, inc))
    # 持续运行，直到计划时间队列变成空为止
    schedule.run()

logging.info("startup scrapy in %s" % time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
timming_exe("scrapy crawlall -s DOWNLOAD_DELAY=2", 24*60*60)
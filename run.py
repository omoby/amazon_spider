# -*- coding:utf-8 -*-
"""
@version: 3.7
@time: 2021/2/28 15:13
@author: James
"""
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR
from apscheduler.schedulers.blocking import BlockingScheduler
import logging.config
from common.config import LOGGING

from requests_item_infos import requests_item_infos_run
from selenium_item_infos import selenium_item_infos_run
from get_proxy import get_proxy_run

# 日志
logging.config.dictConfig(LOGGING)
logger = logging.getLogger('default')

Scheduler = BlockingScheduler()

# 代理
Scheduler.add_job(get_proxy_run, 'interval', minutes=5)
# 爬虫
Scheduler.add_job(requests_item_infos_run, 'cron', hour='0-23', minute=59)


def my_listener(event):
    if event.exception:
        logger.info('The job crashed :(,%s' % event.exception)
    else:
        logger.info('The job worked :)')


Scheduler.add_listener(my_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)

Scheduler.start()

# -*- coding:utf-8 -*-
"""
@version: 3.7
@time: 2021/2/28 13:30
@author: James
"""

import pymysql
from DBUtils.PooledDB import PooledDB
import redis

# 日志配置
LOGGING = {
    # 指明dictConnfig的版本，目前就只有一个版本
    'version': 1,

    # 禁用所有的已经存在的日志配置
    'disable_existing_loggers': False,

    # 格式器
    'formatters': {
        # 详细
        'verbose': {
            'format': '{levelname} {asctime} {filename}=>{funcName} line:{lineno}  message:{message}',
            'style': '{',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        }
    },

    # 处理器
    'handlers': {
        # 按时间进行切割
        'default': {
            'level': 'INFO',
            # 保存到文件，自动切
            'class': 'logging.handlers.TimedRotatingFileHandler',
            # 日志文件
            'filename': "./logs/tract.log",
            # 最多备份几个
            'backupCount': 7,
            'formatter': 'verbose',
            'encoding': 'utf-8',
            # midnight
            "when": "midnight",
            # 经过interval个when, logger自动重建
            'interval': 1
        }

    },
    # 定义记录器
    'loggers': {
        # 默认的logger应用如下配置
        'default': {
            'handlers': ['default'],
            'level': 'DEBUG',
            # 更高级别的logger传递
            'propagate': False
        }

    }
}

# 数据库配置
DATABASES = {
    "db": {
        "host": "",
        "port": 3306,
        "user": "",
        "password": "",
        "database": ""
    }
}

# redis
REDISS = {
    "rs": {
        "host": "",
        "password": "",
        "port": 6379,
        "db": 0
    }
}

DATABASES_CONFIG = DATABASES["db"]
REDISS_CONFIG = REDISS["rs"]

pool = PooledDB(pymysql, 10, host=DATABASES_CONFIG["host"], user=DATABASES_CONFIG["user"],
                passwd=DATABASES_CONFIG["password"], db=DATABASES_CONFIG["database"], port=DATABASES_CONFIG["port"],
                charset='utf8mb4',
                ping=7)

redis_client = redis.Redis(host=REDISS_CONFIG["host"], password=REDISS_CONFIG["password"],
                           port=REDISS_CONFIG["port"],
                           db=REDISS_CONFIG["db"], decode_responses=True)

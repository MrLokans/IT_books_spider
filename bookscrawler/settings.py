import os

BOT_NAME = 'onlinerbooksspider'

SPIDER_MODULES = ['bookscrawler.spiders']
NEWSPIDER_MODULE = 'bookscrawler.spiders'

ITEM_PIPELINES = {'bookscrawler.pipelines.BookFilterPipeline': 100,
                  'bookscrawler.pipelines.ReportPipeline': 150,
                  }

LOG_LEVEL = 'INFO'

MONGODB_SERVER = "localhost"
MONGODB_PORT = 27017
MONGODB_DB = "onliner_books"
MONGODB_COLLECTION = "books"


MAIL_FROM = os.environ['SCRAPY_MAIL_USER']
MAIL_HOST = 'smtp.yandex.ru'
MAIL_PORT = 465
MAIL_SSL = True
MAIL_USER = os.environ['SCRAPY_MAIL_USER']
MAIL_PASS = os.environ['SCRAPY_MAIL_PASS']

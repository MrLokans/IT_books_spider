BOT_NAME = 'onlinerbooksspider'

SPIDER_MODULES = ['bookscrawler.spiders']
NEWSPIDER_MODULE = 'bookscrawler.spiders'

ITEM_PIPELINES = {'bookscrawler.pipelines.BookFilterPipeline': 100,
                  'bookscrawler.pipelines.JsonWithEncodingPipeline': 150,
                  }

LOG_LEVEL = 'INFO'

MONGODB_SERVER = "localhost"
MONGODB_PORT = 27017
MONGODB_DB = "onliner_books"
MONGODB_COLLECTION = "books"

BOT_NAME = 'onlinerbooksspider'

SPIDER_MODULES = ['bookscrawler.spiders']
NEWSPIDER_MODULE = 'bookscrawler.spiders'

ITEM_PIPELINES = ['bookscrawler.pipelines.JsonWithEncodingPipeline',
                  'bookscrawler.pipelines.MongoDBPipeline']

MONGODB_SERVER = "localhost"
MONGODB_PORT = 27017
MONGODB_DB = "onliner_books"
MONGODB_COLLECTION = "books"

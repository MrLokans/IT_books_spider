# Thanks to 'reclosedev' answer on
# https://stackoverflow.com/questions/9181214/scrapy-text-encoding

import json
import io

import pymongo

from scrapy.exceptions import DropItem
from scrapy import log
from scrapy.conf import settings


class MongoDBPipeline(object):

    def __init__(self):
        connection = pymongo.MongoClient(
            settings['MONGODB_SERVER'],
            settings['MONGODB_PORT']
        )
        db = connection[settings['MONGODB_DB']]
        self.collection = db[settings['MONGODB_COLLECTION']]

    def process_item(self, item, spider):
        if item["title"] and item["author"] and item["content"]:
            search_criteria = {
                'title': item['title'],
                'content': item['content'],
                'author': item['content'],
            }
            mongo_item = self.collection.find_one(search_criteria)
            if mongo_item:
                raise DropItem("Item already present.")
            else:
                self.collection.insert(dict(item))
                log.msg("Question added to MongoDB database!",
                        level=log.DEBUG, spider=spider)
        return item


class JsonWithEncodingPipeline(object):

    def __init__(self):
        self.file = io.open('scraped_data_utf8.json', 'w', encoding='utf-8')

    def process_item(self, item, spider):
        line = json.dumps(dict(item), ensure_ascii=False) + "\n"
        self.file.write(line)
        return item

    def spider_closed(self, spider):
        self.file.close()

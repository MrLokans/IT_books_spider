# Thanks to 'reclosedev' answer on
# https://stackoverflow.com/questions/9181214/scrapy-text-encoding

import json
import io
import re

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
        if item is None:
            return
        line = json.dumps(dict(item), ensure_ascii=False) + "\n"
        self.file.write(line)
        return item

    def spider_closed(self, spider):
        self.file.close()


class BookFilterPipeline(object):

    def __init__(self):
        # Words that are filtered for
        self.searched_keywords = ['python', 'javascript',
                                  'программировани[еюя]', 'arduino',
                                  'c\+\+', 'нейронные сети',
                                  'neural networks', 'machine learning',
                                  'машинное обучение', 'data science',
                                  'программировать', 'program', 'programming',
                                  'искусственный интеллект',
                                  'artificial intelligence',
                                  'linux', 'статистика', 'селин', 'хеллер',
                                  'стоккоу', 'гийота', 'git', 'devops',
                                  'компьютерные сети', 'networks',
                                  'angular(?:js)', 'react', 'схемотехника']
        self.search_regex = re.compile(r"|".join(self.searched_keywords),
                                       re.IGNORECASE)

    def appropriate_text(self, text):
        return self.search_regex.search(text)

    def process_item(self, item, spider):
        title_match = self.appropriate_text(item['title'])
        content_match = self.appropriate_text(item['content'])
        if title_match is not None or content_match is not None:
            return item

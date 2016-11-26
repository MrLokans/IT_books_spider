# Thanks to 'reclosedev' answer on
# https://stackoverflow.com/questions/9181214/scrapy-text-encoding

import datetime
import json
import io
import pickle
import re
import mailer
import os

import pymongo

from scrapy.exceptions import DropItem
from scrapy import log
from scrapy.conf import settings

import pandas as pd
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML


class MailSender(object):
    """
    Incapsulates mail sending logics
    """

    def __init__(self, smtphost='localhost', mailfrom='',
                 smtpuser='', smtppass="", smtport=25,
                 smtptls=False, smtpssl=False):
        self.host = smtphost
        self.mailfrom = mailfrom
        self.user = smtpuser
        self.password = smtppass
        self.port = smtport
        self.use_tls = smtptls
        self.use_ssl = smtpssl

    def send(self, to=(), subject="",
             body="", attachs=(), mime='text/plain'):
        message = mailer.Message(From=self.mailfrom,
                                 To=to,
                                 Subject=body)
        message.Body = body

        sender = mailer.Mailer(self.host, port=self.port, use_tls=self.use_tls,
                               use_ssl=self.use_ssl, usr=self.user,
                               pwd=self.password)
        for fname, mime_type, fp in attachs:
            message.attach(fname)
        sender.send(message)

    @classmethod
    def from_settings(cls, settings):
        return cls(smtphost=settings['MAIL_HOST'],
                   smtport=settings['MAIL_PORT'],
                   mailfrom=settings['MAIL_FROM'],
                   smtpuser=settings['MAIL_USER'],
                   smtppass=settings['MAIL_PASS'],
                   smtpssl=settings['MAIL_SSL'])


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
                                  'angular(?:js)', 'react', 'схемотехника',
                                  ]
        self.search_regex = re.compile(r"|".join(self.searched_keywords),
                                       re.IGNORECASE)

    def appropriate_text(self, text):
        return self.search_regex.search(text)

    def process_item(self, item, spider):
        whole_text = item['title'] + item['content']

        match = self.appropriate_text(whole_text)
        if match is not None:
            item['tags'] = [match.group()]
            return item


class ReportPipeline(object):
    MINIMUM_REPORTED_URLS = 5
    URL_CACHE_FILE = 'reported-links.pickle'
    TEMPLATE_NAME = 'report.html'

    def __init__(self):
        self.reported_links = {}
        self.env = Environment(loader=FileSystemLoader(os.path.dirname(__file__)))
        self.mailer = MailSender.from_settings(settings)
        self.send_to = os.environ['SCRAPY_SEND_MAIL_TO']

    def open_spider(self, spider):
        self.reported_links = self.read_url_cache(self.URL_CACHE_FILE)

    def close_spider(self, spider):
        if len(self.reported_links) >= self.MINIMUM_REPORTED_URLS:
            self.dump_cache(self.reported_links, self.URL_CACHE_FILE)
            report_name = self.generate_report_name(report_type='pdf')
            self.generate_pdf_report(self.reported_links, report_name)
            self.email_report(report_name)

    def _get_template(self):
        """
        Reads jinja2 template from file
        """
        return self.env.get_template(self.TEMPLATE_NAME)

    def process_item(self, item, spider):
        if item is None:
            return None
        if not self.is_link_already_reported(item['url']):
            self.reported_links[item['url']] = item
        return item

    def is_link_already_reported(self, url):
        """
        Checks if item with the given
        URL has already been reported
        """
        return url in self.reported_links

    def read_url_cache(self, cache_file: str) -> dict:
        """
        Attempts to read pickled URL cache
        """
        if not os.path.exists(cache_file) or not os.path.isfile(cache_file):
            return {}
        with open(cache_file, 'rb') as f:
            return pickle.load(f)

    def dump_cache(self, reported_links: dict,
                   cache_file: str) -> None:
        """
        Serialize visited links and persist
        """
        with open(cache_file, 'wb') as f_out:
            pickle.dump(reported_links, f_out)

    @staticmethod
    def generate_report_name(now: datetime.datetime=None,
                             report_type: str='pdf',
                             date_format="%Y-%m-%d_%H-%M") -> str:
        """
        Generates report name based on the current date
        """
        if now is None:
            now = datetime.datetime.utcnow()
        formatted_date = now.strftime(date_format)

        return 'Books_report_for_{}.{}'.format(formatted_date, report_type)

    def generate_table_html(self, items: dict,
                            columns: tuple=('url', 'title')) -> str:
        """
        Generates HTML table for the given dictionary item

        :param items: dictionary where the ky is the post URL
        and the value is the corresponding post dictionary
        """
        item_list = [v for _, v in items.items()]
        df = pd.DataFrame(data=item_list, columns=columns)
        return df.to_html()

    def generate_pdf_report(self, items: dict,
                            output_file: str) -> str:
        """
        Generate PDF report from the given list
        of items
        """
        template_context = {
            'report_date': 'today',
            'books_table': items
        }
        template = self._get_template()
        result_html = template.render(template_context)
        HTML(string=result_html).write_pdf(output_file)
        return output_file

    def email_report(self, report_file: str):
        """
        Sends the given PDF report via the given
        reporter class
        """
        with open(report_file, 'rb') as f:
            attach = (report_file, 'application/pdf', f)
            self.mailer.send(to=[self.send_to], subject='Daily book report',
                             body='', attachs=(attach, ))

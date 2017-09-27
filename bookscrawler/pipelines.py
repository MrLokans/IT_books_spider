# Thanks to 'reclosedev' answer on
# https://stackoverflow.com/questions/9181214/scrapy-text-encoding

import datetime
import json
import io
import logging
import mailer
import os
import pickle
import re

from scrapy.conf import settings

import pandas as pd
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSS_PATH = os.path.join(BASE_DIR, 'style.css')


logger = logging.getLogger()


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
                                 Subject=subject)
        message.Body = body

        sender = mailer.Mailer(self.host, port=self.port, use_tls=self.use_tls,
                               use_ssl=self.use_ssl, usr=self.user,
                               pwd=self.password)
        for fname, mime_type, fp in attachs:
            message.attach(fname)
        sender.send(message)

    @classmethod
    def from_settings(cls, settings):
        user = settings['MAIL_USER']
        password = settings['MAIL_PASS']
        recipient = settings['MAIL_FROM']
        if not any([user, password, recipient]):
            raise ValueError("Mail credentials missing.")
        return cls(smtphost=settings['MAIL_HOST'],
                   smtport=settings['MAIL_PORT'],
                   mailfrom=recipient,
                   smtpuser=user,
                   smtppass=password,
                   smtpssl=settings['MAIL_SSL'])


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

    def open_spider(self, spider):
        searched_keywords = spider.settings['SEARCHED_KEYWORDS']
        self.search_regex = re.compile(r"|".join(searched_keywords),
                                       re.IGNORECASE)

    def appropriate_text(self, text):
        return self.search_regex.search(text)

    def process_item(self, item, spider):
        whole_text = item['title'] + item['content']

        match = self.appropriate_text(whole_text)
        if match is not None:
            logger.debug("Match found: {}".format(match.group()))
            item['tags'] = [match.group()]
            return item


class ReportPipeline(object):
    MINIMUM_REPORTED_URLS = 5
    URL_CACHE_FILE = 'reported-links.pickle'
    TEMPLATE_NAME = 'report.html'

    def __init__(self):
        self.reported_links = {}
        self._template_dir = self._get_template_dir()
        self.env = Environment(loader=FileSystemLoader(self._template_dir))
        self.mailer = MailSender.from_settings(settings)
        self.send_to = os.environ['SCRAPY_SEND_MAIL_TO']
        self.to_be_reported = {}

    def open_spider(self, spider):
        self.reported_links = self.read_url_cache(self.URL_CACHE_FILE)

    def close_spider(self, spider):
        self.dump_cache(self.reported_links, self.URL_CACHE_FILE)
        report_name = self.generate_report_name(report_type='pdf')
        self.generate_pdf_report(self.to_be_reported, report_name)
        self.email_report(report_name)

    def _get_template_dir(self):
        return os.path.dirname(__file__)

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
            self.to_be_reported[item['url']] = item
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
        report_name = 'Books_report_for_{}.{}'.format(formatted_date,
                                                      report_type)
        logger.info("Report name generated: {}.".format(report_name))
        return report_name

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
            'items_table': items
        }
        template = self._get_template()
        result_html = template.render(template_context)
        HTML(string=result_html).write_pdf(output_file,
                                           stylesheets=[CSS_PATH])
        return output_file

    def email_report(self, report_file: str):
        """
        Sends the given PDF report via the given
        reporter class
        """
        with open(report_file, 'rb') as f:
            attach = (report_file, 'application/pdf', f)
            logger.info("Sending report to {}".format(self.send_to))
            self.mailer.send(to=[self.send_to],
                             subject='[it-book-spider] Daily book report',
                             body='', attachs=(attach, ))

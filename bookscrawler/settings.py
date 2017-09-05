import os

BOT_NAME = 'onlinerbooksspider'

SPIDER_MODULES = ['bookscrawler.spiders']
NEWSPIDER_MODULE = 'bookscrawler.spiders'

ITEM_PIPELINES = {'bookscrawler.pipelines.BookFilterPipeline': 100,
                  'bookscrawler.pipelines.ReportPipeline': 150,
                  }

# DOWNLOADER_MIDDLEWARES = {
#     'bookscrawler.middlewares.PageCachingMiddleware': 100
# }

SEARCHED_KEYWORDS = ['python', 'javascript',
                     'программировани[еюя]', 'программируем',
                     'программист', 'arduino',
                     'c\+\+', 'нейронные сети', 'разработка',
                     'neural networks', 'machine learning',
                     'машинное обучение', 'data science',
                     'program', 'programming',
                     'искусственный интеллект',
                     'artificial intelligence',
                     'linux', 'статистика', 'селин', 'хеллер',
                     'стоккоу', 'гийота', 'git\s', 'devops',
                     'компьютерные сети', 'networks',
                     'angular(?:js)', 'react', 'схемотехника',
                     'алгоритм', 'algorithm', 'java', 'комикс',
                     'sandman', 'песочный человек', 'ноктюрны']

if os.path.exists('/var/log/it-spider'):
    LOGGING_DIR = '/var/log/it-spider'
else:
    LOGGING_DIR = os.path.dirname(__file__)
LOG_FILE = os.path.join(LOGGING_DIR, 'scrapping.log')
LOG_LEVEL = 'INFO'


MAIL_FROM = os.environ.get('SCRAPY_MAIL_USER')
MAIL_HOST = 'smtp.yandex.ru'
MAIL_PORT = 465
MAIL_SSL = True
MAIL_USER = os.environ.get('SCRAPY_MAIL_USER')
MAIL_PASS = os.environ.get('SCRAPY_MAIL_PASS')

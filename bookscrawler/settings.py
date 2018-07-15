import os

BOT_NAME = 'onlinerbooksspider'

SPIDER_MODULES = ['bookscrawler.spiders']
NEWSPIDER_MODULE = 'bookscrawler.spiders'

ITEM_PIPELINES = {'bookscrawler.pipelines.BookFilterPipeline': 100,
                  'bookscrawler.pipelines.ReportPipeline': 150,
                  }

# ID-s of forums we want to parse
FORUM_IDS = [
    191,  # PS3 games
    203,  # Books
    237,  # Musical instruments
]


PROGRAMMING_KEYWORDS = [
    'python', 'data intensive',
    'алгоритм', 'algorithm',
    'distributed systems',
    'программировани[еюя]',
    'программист', 'нейронные сети', 'разработка',
    'program', 'programming',
    'искусственный интеллект',
    'artificial intelligence',
    'машинное обучение', 'data science',
    'neural networks', 'machine learning',
]

BOOKS_KEYWORDS = [
    'linux', 'статистика', 'селин', 'хеллер',
    'стоккоу', 'гийота', 'devops',
    'схемотехника',
    'комикс',
]

GAME_KEYWORDS = [
    'ps4', 'playstation 4', 'playstation4',
]

MUSIC_KEYWORDS = [
    'fender', 'squier', 'ltd'
]

SEARCHED_KEYWORDS = (
    PROGRAMMING_KEYWORDS +
    BOOKS_KEYWORDS +
    GAME_KEYWORDS +
    MUSIC_KEYWORDS
)

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

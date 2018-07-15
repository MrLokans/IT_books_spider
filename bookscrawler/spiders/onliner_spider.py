import logging
from urllib.parse import urljoin

import requests
from scrapy.selector import Selector
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

from bookscrawler.items import PostItem
from bookscrawler.spiders.url_cache import (
    URLFileCache,
    URLStorageStrategy
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__file__)


BASE_URL = "http://baraholka.onliner.by"
BOOK_FORUM = "viewforum.php?f={}"

POSTS_PER_PAGE = 50

CACHE_FILE = 'visited_urls.pickle'


def get_forum_url_from_id(forum_id):
    return urljoin(BASE_URL, BOOK_FORUM.format(forum_id))


def get_forum_page_url(url, page_number, posts_per_page=POSTS_PER_PAGE):
    return url + "&sk=created&start={}".format(page_number * posts_per_page)


def correct_encoding(s):
    if hasattr(s, "encode"):
        return s.encode('utf-8').decode('utf-8')


class BookSpider(CrawlSpider):
    name = "onlinerbooksspider"
    allowed_domains = ["baraholka.onliner.by"]

    rules = [Rule(
        LinkExtractor(restrict_css="h2.wraptxt"),
        callback='parse_topic_page', follow=True,
        process_request='process_bulletin_link')]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cache = URLFileCache(CACHE_FILE, URLStorageStrategy())
        self.cache.load_cache()

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super().from_crawler(crawler, *args, **kwargs)
        spider._forum_ids = crawler.settings.getlist(
            'FORUM_IDS', []
        )
        spider._calculate_start_urls()
        return spider

    def _extract_number_of_pages_from_pagination(self, body):
        pages = Selector(text=body)\
            .css('ul.pages-fastnav')\
            .xpath('li//text()')\
            .extract()[-1]
        return int(pages)

    def _calculate_start_urls(self):
        self.start_urls = []
        for forum_id in self._forum_ids:
            url = get_forum_url_from_id(forum_id)
            body = requests.get(url).text
            pages = self._extract_number_of_pages_from_pagination(body)
            pages_urls = [
                get_forum_page_url(url, i)
                for i in range(1, pages)
            ]
            self.start_urls.extend(pages_urls)

    def process_bulletin_link(self, request):
        """
        Check whether we've already visited
        the provided URL
        """
        if self.cache.has_url(request.url):
            return None
        self.cache.add_url(request.url)
        return request

    def closed(self, reason):
        self.cache.persist_cache()

    def parse_topic_page(self, response):
        post = PostItem()
        post['url'] = response.url
        post["title"] = self.extract_title(response)
        post["author"] = self.extract_author(response)
        post['price'] = self.extract_price(response)
        post["content"] = self.extract_content(response)
        post["images"] = self.extract_images(response)
        post["created"] = self.extract_created(response)
        post["city"] = self.extract_city(response)
        yield post

    def extract_city(self, response):
        city_selector = "strong.fast-desc-region::text"
        return response.css(city_selector).extract_first().strip()

    def extract_created(self, response):
        created_selector = "//small[@class='msgpost-date']/span[1]//text()"
        return response.xpath(created_selector).extract_first().strip()

    def extract_title(self, response):
        header_title_selector = "h1.m-title-i.title::attr('title')"
        return response.css(header_title_selector).extract_first()

    def extract_author(self, response):
        author_nickname_selector = ".mtauthor-nickname a._name::attr('title')"
        return response.css(author_nickname_selector).extract_first()

    def extract_price(self, response):
        price_selector = "li.price-primary::text"
        price = response.css(price_selector).extract_first()
        if price is not None:
            price = price.strip()
        return price

    def extract_content(self, response):
        content_selector = "//div[@class='content']/p/text()"
        content = response.xpath(content_selector).extract()
        if isinstance(content, list):
            content = "".join(p.strip("\r\n") for p in content)
        return content

    def extract_images(self, response):
        img_selector = "img.msgpost-img::attr('src')"
        return [i for i in response.css(img_selector).extract()]

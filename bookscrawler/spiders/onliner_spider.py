from urllib.parse import urljoin

import scrapy

from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
# from scrapy.selector import Selector

from bookscrawler.items import PostItem

BASE_URL = "http://baraholka.onliner.by"
BOOK_FORUM = "viewforum.php?f=203"

START_URL = urljoin(BASE_URL, BOOK_FORUM)
PAGE_NUMBER_URL = START_URL + "&sk=created&start={}"
PAGE_2_URL = START_URL + "&sk=created&start=50"

# Here for simplicity sake only 20 pages are being parsed.
# The better way is to obtain pagination widget and count the number
# of total post pages.

POSTS_PER_PAGE = 90

PAGES_COUNT = 40
PAGES_URLS = [
    PAGE_NUMBER_URL.format(x * POSTS_PER_PAGE)
    for x in range(2, PAGES_COUNT)
]


def correct_encoding(s):
    if hasattr(s, "encode"):
        return s.encode('utf-8').decode('utf-8')


class BookSpider(CrawlSpider):
    name = "onlinerbooksspider"
    allowed_domains = ["baraholka.onliner.by"]
    start_urls = [START_URL]
    start_urls.extend(PAGES_URLS)

    rules = [Rule(
        LinkExtractor(restrict_css="h2.wraptxt"),
        callback='parse_topic_page', follow=True)]

    def parse_topic_page(self, response):
        header_title_selector = "h1.m-title-i.title::attr('title')"
        author_nickname_selector = ".mtauthor-nickname a._name::attr('title')"
        content_selector = "//div[@class='content']/p/text()"
        img_selector = "img.msgpost-img::attr('src')"

        post = PostItem()
        post["title"] = response.css(header_title_selector).extract_first()
        post["author"] = response.css(author_nickname_selector).extract_first()
        post["content"] = response.xpath(content_selector).extract()
        post["images"] = [i for i in response.css(img_selector).extract()]
        yield post

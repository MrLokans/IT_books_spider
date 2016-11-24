from urllib.parse import urljoin

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

PAGES_COUNT = 140
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
        post = PostItem()
        post['url'] = response.url
        post["title"] = self.extract_title(response)
        post["author"] = self.extract_author(response)
        post['price'] = self.extract_price(response)
        post["content"] = self.extract_content(response)
        post["images"] = self.extract_images(response)
        yield post

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

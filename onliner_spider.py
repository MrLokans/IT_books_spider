import scrapy

from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
# from scrapy.selector import Selector

from items import PostItem

BASE_URL = "http://baraholka.onliner.by"
BOOK_FORUM = "viewforum.php?f=203"

START_URL = BASE_URL + '/' + BOOK_FORUM
PAGE_NUMBER_URL = START_URL + "&sk=created&start={}"
PAGE_2_URL = START_URL + "&sk=created&start=50"

# Here for simplicity sake only 20 pages are being parsed.
# The better way is to obtain pagination widget and count the number
# of total post pages.
PAGES_COUNT = 5
PAGES_URLS = [
    PAGE_NUMBER_URL.format(x * 50) for x in range(2, PAGES_COUNT)
]


class BookSpider(CrawlSpider):
    name = "onlinerbooksspider"
    start_urls = [START_URL]
    start_urls.extend(PAGES_URLS)

    # rules = [Rule(
    #     LinkExtractor(restrict_css="h2.wraptxt a::attr('href')"),
    #     callback='parse_topic_page')]

    def parse(self, response):
        topic_url_selector = "h2.wraptxt a::attr('href')"
        # first_page = NEWS_URL + 'page/1'

        for page_url in response.css(topic_url_selector).extract():
            yield scrapy.Request(response.urljoin(page_url),
                                 self.parse_topic_page)

    def parse_topic_page(self, response):
        header_title_selector = "h1.m-title-i.title::attr('title')"
        author_nickname_selector = ".mtauthor-nickname a._name::attr('title')"
        content_selector = "div.content"
        img_selector = "img.msgpost-img::attr('src')"

        post = PostItem()
        post["title"] = response.css(header_title_selector).extract()
        post["author"] = response.css(author_nickname_selector).extract()
        post["content"] = response.css(content_selector).extract()
        post["images"] = []
        for img in response.css(img_selector).extract():
            post["images"].append(img)

        yield post

from scrapy.item import Item, Field


class PostItem(Item):
    title = Field()
    author = Field()
    content = Field()
    link = Field()
    updated = Field()
    created = Field()
    city = Field()
    price = Field()
    buy_or_sell = Field()
    images = Field()

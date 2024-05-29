from scrapy.item import Field, Item


class URLItem(Item):
    url = Field()

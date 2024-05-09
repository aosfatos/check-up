import scrapy


class AdItem(scrapy.Item):
    title = scrapy.Field()
    external_link = scrapy.Field()
    thumbnail = scrapy.Field()
    tag = scrapy.Field()
    original_url = scrapy.Field()

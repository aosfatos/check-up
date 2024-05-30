import scrapy


class BaseSpider(scrapy.Spider):
    custom_settings = {
        "DEPTH_LIMIT": 1,
    }

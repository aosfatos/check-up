import scrapy

from spiders.base import BaseSpider
from spiders.items import URLItem


class EstadaoSpider(BaseSpider):
    name = "estadaospider"
    start_urls = ["https://www.estadao.com.br/"]
    allowed_domains = ["estadao.com.br"]

    def allow_url(self, entry_url):
        return entry_url.startswith("https://www.estadao.com.br") and len(entry_url) > 100

    def parse(self, response):
        url_item = URLItem()
        for entry in response.css("a"):
            url = entry.attrib.get("href")
            if url and self.allow_url(url):
                url_item["url"] = url
                yield url_item
                yield scrapy.Request(url=url, callback=self.parse)

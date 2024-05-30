import scrapy

from spiders.base import BaseSpider
from spiders.items import URLItem


class FolhaSpider(BaseSpider):
    name = "folhaspider"
    start_urls = ["https://www.folha.uol.com.br/"]
    allowed_domains = ["folha.uol.com.br"]

    def allow_url(self, entry_url):
        return "www1.folha.uol.com.br" in entry_url and len(entry_url) > 100

    def parse(self, response):
        url_item = URLItem()
        for entry in response.css(".c-headline__url"):
            url = entry.attrib.get("href")
            if url and self.allow_url(url):
                url_item["url"] = url
                yield url_item
                yield scrapy.Request(url=url, callback=self.parse)

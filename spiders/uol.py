import re

import scrapy

from spiders.base import BaseSpider
from spiders.items import URLItem


class UOLSpider(BaseSpider):
    name = "uolspider"
    start_urls = ["https://www.uol.com.br/"]
    allowed_domains = ["uol.com.br/"]

    def allow_url(self, entry_url):
        return (
            re.match(r'https://(www|economia|noticias|educacao).uol.com.br', entry_url)
            and len(entry_url) > 100
            and "utm_source" not in entry_url
        )

    def parse(self, response):
        url_item = URLItem()
        for entry in response.css("a"):
            url = entry.attrib.get("href")
            if url and self.allow_url(url):
                url_item["url"] = url
                yield url_item
                yield scrapy.Request(url=url, callback=self.parse)

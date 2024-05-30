import scrapy

from spiders.base import BaseSpider
from spiders.items import URLItem


class RBSSpider(BaseSpider):
    name = "rbsspider"
    start_urls = ["https://www.clicrbs.com.br/"]
    allowed_domains = ["clicrbs.com.br"]

    def allow_url(self, entry_url):
        return (
            len(entry_url) > 100
            and entry_url.startswith("https://gauchazh.clicrbs.com.br")
        )

    def parse(self, response):
        url_item = URLItem()
        for entry in response.css("a"):
            url = entry.attrib.get("href")
            if url and self.allow_url(url):
                url_item["url"] = url
                yield url_item
                yield scrapy.Request(url=url, callback=self.parse)

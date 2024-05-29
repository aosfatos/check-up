import scrapy

from spiders.items import URLItem


class GloboSpider(scrapy.Spider):
    name = "globospider"
    start_urls = ["https://oglobo.globo.com/"]
    allowed_domains = ["oglobo.globo.com/"]
    custom_settings = {
        "DEPTH_LIMIT": 2,
    }

    def allow_url(self, entry_url):
        return len(entry_url) > 100 and entry_url.startswith("https://oglobo.globo.com")

    def parse(self, response):
        url_item = URLItem()
        for entry in response.css("a"):
            url = entry.attrib.get("href")
            if url and self.allow_url(url):
                url_item["url"] = url
                yield url_item
                yield scrapy.Request(url=url, callback=self.parse)

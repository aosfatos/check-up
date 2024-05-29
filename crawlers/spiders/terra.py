import scrapy

from spiders.items import URLItem


class TerraSpider(scrapy.Spider):
    name = "terraspider"
    start_urls = ["https://www.terra.com.br/"]
    allowed_domains = ["terra.com.br"]
    custom_settings = {
        "DEPTH_LIMIT": 1,
    }

    def allow_url(self, entry_url):
        return True

    def parse(self, response):
        url_item = URLItem()
        for entry in response.css(".main-url"):
            url = entry.attrib.get("href")
            if url and self.allow_url(url):
                url_item["url"] = url
                yield url_item
                yield scrapy.Request(url=url, callback=self.parse)

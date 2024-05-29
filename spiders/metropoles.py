import scrapy

from items import URLItem


class MetropolesSpider(scrapy.Spider):
    name = "metropolesspider"
    start_urls = ["https://www.metropoles.com/"]
    allowed_domains = ["metropoles.com"]
    custom_settings = {
        "DEPTH_LIMIT": 2,
    }

    def allow_url(self, entry_url):
        return True

    def parse(self, response):
        url_item = URLItem()
        for entry in response.css(".noticia__titulo > a"):
            url = entry.attrib.get("href")
            if url and self.allow_url(url):
                url_item["url"] = url
                yield url_item
                yield scrapy.Request(url=url, callback=self.parse)

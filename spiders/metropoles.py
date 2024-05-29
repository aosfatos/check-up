import scrapy


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
        for entry in response.css(".noticia__titulo > a"):
            url = entry.attrib.get("href")
            if url and self.allow_url(url):
                yield {"url": url}
                yield scrapy.Request(url=url, callback=self.parse)

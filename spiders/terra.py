import scrapy


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
        for entry in response.css(".main-url"):
            url = entry.attrib.get("href")
            if url and self.allow_url(url):
                yield {"url": url}
                yield scrapy.Request(url=url, callback=self.parse)

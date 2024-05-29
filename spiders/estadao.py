import scrapy


class EstadaoSpider(scrapy.Spider):
    name = "estadaospider"
    start_urls = ["https://www.estadao.com.br/"]
    allowed_domains = ["estadao.com.br"]
    custom_settings = {
        "DEPTH_LIMIT": 1,
    }

    def allow_url(self, entry_url):
        return entry_url.startswith("https://www.estadao.com.br") and len(entry_url) > 100

    def parse(self, response):
        for entry in response.css("a"):
            url = entry.attrib.get("href")
            if url and self.allow_url(url):
                yield {"url": url}
                yield scrapy.Request(url=url, callback=self.parse)

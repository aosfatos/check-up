import scrapy


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
        for entry in response.css("a"):
            url = entry.attrib.get("href")
            if url and self.allow_url(url):
                yield {"url": url}
                yield scrapy.Request(url=url, callback=self.parse)

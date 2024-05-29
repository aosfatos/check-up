import scrapy


class FolhaSpider(scrapy.Spider):
    name = "folhaspider"
    start_urls = ["https://www.folha.uol.com.br/"]
    allowed_domains = ["folha.uol.com.br"]
    custom_settings = {
        "DEPTH_LIMIT": 2,
    }

    def allow_url(self, entry_url):
        return "www1.folha.uol.com.br" in entry_url and len(entry_url) > 100

    def parse(self, response):
        for entry in response.css(".c-headline__url"):
            url = entry.attrib.get("href")
            if url and self.allow_url(url):
                yield {"url": url}
                yield scrapy.Request(url=url, callback=self.parse)

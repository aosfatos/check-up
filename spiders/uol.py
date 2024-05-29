import re

import scrapy


class UOLSpider(scrapy.Spider):
    name = "uolspider"
    start_urls = ["https://www.uol.com.br/"]
    allowed_domains = ["uol.com.br/"]
    custom_settings = {
        "DEPTH_LIMIT": 2,
    }

    def allow_url(self, entry_url):
        return (
            re.match(r'https://(www|economia|noticias|educacao).uol.com.br', entry_url)
            and len(entry_url) > 100
            and "utm_source" not in entry_url
        )

    def parse(self, response):
        for entry in response.css("a"):
            url = entry.attrib.get("href")
            if url and self.allow_url(url):
                yield {"url": url}
                yield scrapy.Request(url=url, callback=self.parse)

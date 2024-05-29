import scrapy

from spiders.items import URLItem


class VejaSpider(scrapy.Spider):
    name = "vejaspider"
    start_urls = ["https://veja.abril.com.br/"]
    allowed_domains = ["veja.abril.com.br"]
    custom_settings = {
        "DEPTH_LIMIT": 1,
    }

    def allow_url(self, entry_url):
        return (
            entry_url.startswith("https://veja.abril.com.br")
            and len(entry_url) > 100
            and not entry_url.startswith("https://veja.abril.com.br/ofertas")
        )

    def parse(self, response):
        url_item = URLItem()
        for entry in response.css("a"):
            url = entry.attrib.get("href")
            if url and self.allow_url(url):
                url_item["url"] = url
                yield url_item
                yield scrapy.Request(url=url, callback=self.parse)

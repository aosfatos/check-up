import scrapy


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
        for entry in response.css("a"):
            url = entry.attrib.get("href")
            if url and self.allow_url(url):
                yield {"url": url}
                yield scrapy.Request(url=url, callback=self.parse)

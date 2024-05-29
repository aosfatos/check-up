import scrapy


class RBSSpider(scrapy.Spider):
    name = "rbsspider"
    start_urls = ["https://www.clicrbs.com.br/"]
    allowed_domains = ["clicrbs.com.br"]
    custom_settings = {
        "DEPTH_LIMIT": 1,
    }

    def allow_url(self, entry_url):
        return (
            len(entry_url) > 100
            and entry_url.startswith("https://gauchazh.clicrbs.com.br")
        )

    def parse(self, response):
        for entry in response.css("a"):
            url = entry.attrib.get("href")
            if url and self.allow_url(url):
                yield {"url": url}
                yield scrapy.Request(url=url, callback=self.parse)

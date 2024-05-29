import re

import scrapy


class IGSpider(scrapy.Spider):
    name = "igspider"
    start_urls = ["https://www.ig.com.br/"]
    allowed_domains = ["ig.com.br"]
    custom_settings = {
        "DEPTH_LIMIT": 1,
    }

    def allow_url(self, entry_url):
        return (
            len(entry_url) > 100
            and re.match(
                r"https://(ultimosegundo|economia|queer|gente|delas|esporte|carros|"
                r"canaldopet|receitas|tecnologia|play|turismo|odia).ig.com.br",
                entry_url,
            )
        )

    def parse(self, response):
        for entry in response.css("a"):
            url = entry.attrib.get("href")
            if url and self.allow_url(url):
                yield {"url": url}
                yield scrapy.Request(url=url, callback=self.parse)

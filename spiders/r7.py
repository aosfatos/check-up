import re

import scrapy


class R7Spider(scrapy.Spider):
    name = "r7spider"
    start_urls = ["https://www.r7.com/"]
    allowed_domains = ["r7com"]
    custom_settings = {
        "DEPTH_LIMIT": 2,
    }

    def allow_url(self, entry_url):
        return (
            len(entry_url) > 100
            and re.match(
                r"https://(entretenimento|esportes|record|noticias).r7.com",
                entry_url,
            )
        )

    def parse(self, response):
        for entry in response.css("a"):
            url = entry.attrib.get("href")
            if url and self.allow_url(url):
                yield {"url": url}
                yield scrapy.Request(url=url, callback=self.parse)

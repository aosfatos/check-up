import logging

import scrapy
from scrapy_playwright.page import PageMethod

from base import BaseSpider


class VejaSpider(BaseSpider):
    name = "veja"
    url = "https://veja.abril.com.br/"
    allowed_domains = ["veja.abril.com.br"]

    def start_requests(self):
        yield scrapy.Request(
           self.url,
           meta=dict(
               playwright=True,
               playwright_include_page=True,
               errback=self.errback,
               playwright_page_methods=[
                   # PageMethod("screenshot", path="example.png", full_page=True),
                   PageMethod("wait_for_load_state", "load"),
               ],
           ),
        )

    async def parse(self, response):
        page = response.meta["playwright_page"]
        await page.wait_for_load_state("load")
        entries = response.xpath("//a[contains(@class,'card b')]")[:20]
        if "coluna" in response.url:
            mgbox = await page.query_selector(".mgbox")
            if mgbox:
                hrefs = []
                rows = await mgbox.query_selector_all(".allink")
                for row in rows:
                    hrefs.append(await rows[0].get_attribute("href"))

        for entry in entries:
            if entry_url := entry.attrib.get("href"):
                yield scrapy.Request(
                   entry_url,
                   meta=dict(
                       playwright=True,
                       playwright_include_page=True,
                       errback=self.errback,
                       playwright_page_methods=[
                           # PageMethod("screenshot", path="example.png", full_page=True),
                           # PageMethod("wait_for_load_state", "domcontentloaded"),
                       ],
                   ),
                )

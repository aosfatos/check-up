import logging

import scrapy
from scrapy_playwright.page import PageMethod
from playwright.sync_api import TimeoutError as PlayWrightTimeoutError

from base import BaseSpider


class VejaSpider(BaseSpider):
    name = "folha"
    allowed_domains = ["folha.uol.com.br"]
    url = "https://www1.folha.uol.com.br/cotidiano/2024/05/ong-cria-abrigos-para-pessoas-com-autismo-no-rio-grande-do-sul.shtml"

    async def parse_taboola(self, response, original_url):
        links_content = response.css(".c-taboola")
        for link_content in links_content:
            title = link_content.xpath('.//div[@data-item-title]/@data-item-title').get()
            external_link = link_content.xpath(".//a").attrib["href"]
            thumbnail = link_content.xpath('.//div[@data-item-thumb]/@data-item-thumb').get()
            tag = link_content.css(".inline-branding::text").get()
            yield {
                "title": title,
                "external_link": external_link,
                "thumbnail": thumbnail,
                "tag": tag,
                "original_url": original_url,
            }

    def start_requests(self):
        yield scrapy.Request(
           self.url,
           meta=dict(
               playwright=True,
               playwright_include_page=True,
               errback=self.errback,
               playwright_page_methods=[
                   PageMethod('wait_for_timeout', 50_000),
                   PageMethod("wait_for_load_state", "load"),
               ],
           ),
        )

    async def parse(self, response):
        page = response.meta["playwright_page"]
        await page.wait_for_load_state("load")
        try:
            await page.wait_for_selector("#taboola-below-article-thumbnails", timeout=5_000)
        except PlayWrightTimeoutError:
            logging.error(f"PlayWrightTimeoutError: {response.url}")
            return

        links_content = response.css(".c-taboola")
        for link_content in links_content:
            title = link_content.xpath('.//div[@data-item-title]/@data-item-title').get()
            external_link = link_content.xpath(".//a").attrib["href"]
            thumbnail = link_content.xpath('.//div[@data-item-thumb]/@data-item-thumb').get()
            tag = link_content.css(".inline-branding::text").get()
            # if tag is None and "madonna" not in title.lower():
            #     1 / 0
            yield {
                "title": title,
                "external_link": external_link,
                "thumbnail": thumbnail,
                "tag": tag,
                "original_url": response.url,
            }

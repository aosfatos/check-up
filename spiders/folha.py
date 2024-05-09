import logging
import time
from datetime import datetime

import pytz
import scrapy
from scrapy_playwright.page import PageMethod
from playwright.sync_api import TimeoutError as PlayWrightTimeoutError

from base import BaseSpider
from items import AdItem


class VejaSpider(BaseSpider):
    name = "folha"
    url = "https://www1.folha.uol.com.br"
    allowed_domains = ["folha.uol.com.br"]
    # url = "https://www1.folha.uol.com.br/colunas/viniciustorres/2024/05/alem-dos-retirantes-das-secas-teremos-os-retirantes-das-enchentes.shtml"

    def get_tag(self, content):
        tag = None
        for css_selector in [".inline-branding", ".branding"]:
            tag = content.css(f"{css_selector}::text").get()
            if tag:
                break

        return tag

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
               # playwright_page_methods=[
               #     PageMethod('wait_for_timeout', 50_000),
               #     PageMethod("wait_for_load_state", "load"),
               # ],
           ),
        )

    async def parse(self, response):
        page = response.meta["playwright_page"]
        await page.wait_for_load_state("load")
        entries = response.xpath("//a[contains(@class,'__url')]")[:50]
        logging.info(f"FOUND {len(entries)} entries...")
        for entry in entries:
            if entry_url := entry.attrib.get("href"):
                logging.info(f"Yielding {entry_url}")
                yield scrapy.Request(
                   entry_url,
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
        if response.url not in ["https://www.folha.uol.com.br/"]:
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
                logging.info(f"Saving data from {external_link}...")
                tag = self.get_tag(link_content)
                logging.info(f"TITLE {title}")
                yield AdItem(
                    title=title,
                    external_link=external_link,
                    thumbnail=thumbnail,
                    tag=tag,
                    original_url=response.url,
                )

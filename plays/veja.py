import time

from decouple import config
from loguru import logger
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError, sync_playwright

from plays.base import BasePlay
from plays.items import AdItem, EntryItem
from plays.utils import get_or_none


class VejaPlay(BasePlay):
    name = "veja"
    n_expected_ads = 13

    @classmethod
    def match(cls, url):
        return "veja.abril.com.br" in url

    @property
    def proxy(self):
        return {
            "server": config("OXYLABS_PROXY_SERVER"),
            "username": config("OXYLABS_USERNAME"),
            "password": config("OXYLABS_PASSWORD"),
        }

    def find_items_mgid_page(self, html_content, element_content) -> AdItem:
        return AdItem(
            title=get_or_none(r"<title>(.*?)</title>", html_content),
            url=get_or_none(r'</script>\n<a href="(.*?)"', html_content),
            thumbnail_url=get_or_none(r'data-src="(.*?)"', element_content),
            tag=get_or_none(
                r'<div class="mcdomain"><a[^>]+>(.*?)<\/a><\/div>',
                element_content
            ),
        )

    def find_items(self, html_content, element_content) -> AdItem:
        return AdItem(
            title=get_or_none(r'<h1 class="title">(.*?)</h1>', html_content),
            url=get_or_none(r'href="(.*?)"', element_content),
            thumbnail_url=get_or_none(r'data-src="(.*?)"', element_content),
            tag=None,
        )

    def parse_elements(self, elements):
        n_elements = elements.count()
        elements_row = []
        for i in range(n_elements):
            current_element = elements.nth(i)
            if current_element.inner_text() == "":
                continue
            elements_row.append(current_element)

        return elements_row

    def get_hrefs(self, elements):
        hrefs = []
        for ele in elements:
            try:
                logger.info(f"Getting href attribute from '{ele}'")
                href = ele.locator("a").first.get_attribute("href")
                logger.info(f"Got '{href}'")
                hrefs.append(href)
            except PlaywrightTimeoutError:
                logger.error(f"Error getting href from {ele}")

        return hrefs

    def pre_run(self):
        pass

    def run(self) -> EntryItem:
        with sync_playwright() as p:
            browser = self.launch_browser(p)
            page = browser.new_page()
            logger.info(f"[{self.name}] Opening URL '{self.url}'...")
            # Increase timeout to account for potential delays introduced by the proxy
            page.goto(self.url, timeout=180_000)  # 180s
            logger.info(f"[{self.name}] Searching for ads...")
            time.sleep(self.wait_time)
            page.locator(".mgbox").scroll_into_view_if_needed()
            time.sleep(self.wait_time)

            entry_title = page.locator("h1.title").inner_text()

            elements = page.locator(".mgline")
            entry_screenshot_path = self.take_screenshot(page, self.url, goto=False)

            elements = self.parse_elements(elements)
            hrefs = self.get_hrefs(elements)
            page = browser.new_page()
            ad_items = []
            for element, href in zip(elements, hrefs):
                logger.info(f"Opening AD URL '{href}'")
                page.goto(href, timeout=60_000)
                time.sleep(self.wait_time)
                logger.info(f"Getting page content '{href}'")
                page_content = page.content()
                element_content = element.inner_html()
                try:
                    page.locator(".news__image_big").inner_html()
                    ad_items.append(self.find_items_mgid_page(page_content, element_content))
                except PlaywrightTimeoutError:
                    ad_items.append(self.find_items(page_content, element_content))

            logger.info("Done")
            return EntryItem(
                title=entry_title,
                url=self.url,
                screenshot_path=entry_screenshot_path,
                ads=ad_items,
            )

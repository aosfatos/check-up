import time

from decouple import config
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError, sync_playwright

from plays.base import BasePlay
from plays.items import AdItem, EntryItem
from plays.utils import get_or_none
from plog import logger


class VejaPlay(BasePlay):
    name = "veja"
    n_expected_ads = 10

    @classmethod
    def match(cls, url):
        return "veja.abril.com.br" in url

    @classmethod
    def get_options(cls):
        return {"proxy": {"server": "socks5://tor:9050"}}

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

            elements_content = [ele.inner_html() for ele in elements]

            ad_items = []
            for element_content, href in zip(elements_content, hrefs):
                logger.info(f"[{self.name}] Opening AD URL '{href}'")

                # TODO: create `goto` method that has an option to not raise timeout exception
                try:
                    page.goto(href, timeout=90_000)
                except PlaywrightTimeoutError as exc:
                    logger.warning(f"[{self.name}] {exc}")
                    continue

                time.sleep(self.wait_time)
                logger.info(f"[{self.name}] Getting page content '{href}'")
                page_content = page.content()
                try:
                    page.locator(".news__image_big").inner_html()
                    ad_items.append(self.find_items_mgid_page(page_content, element_content))
                except PlaywrightTimeoutError:
                    ad_items.append(self.find_items(page_content, element_content))

            logger.info(f"[{self.name}] Done")
            return EntryItem(
                title=entry_title,
                url=self.url,
                screenshot_path=entry_screenshot_path,
                ads=ad_items,
            )

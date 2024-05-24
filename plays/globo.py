import time

from decouple import config
from loguru import logger
from playwright.sync_api import sync_playwright

from plays.base import BasePlay
from plays.items import AdItem, EntryItem
from plays.utils import get_or_none


class GloboPlay(BasePlay):
    name = "globo"

    @classmethod
    def match(cls, url):
        return "oglobo.globo.com/" in url

    def find_items(self, html_content) -> AdItem:
        return AdItem(
            title=get_or_none(r'title="(.*?)"', html_content),
            url=get_or_none(r'href="(.*?)"', html_content),
            thumbnail_url=get_or_none(r'url\(&quot;(.*?)&quot;\)', html_content),
            tag=get_or_none(r'<span class="branding-inner".*?>(.*?)<\/span>', html_content),
        )

    @property
    def proxy(self):
        return {
            "server": config("OXYLABS_PROXY_SERVER"),
            "username": config("OXYLABS_USERNAME"),
            "password": config("OXYLABS_PASSWORD"),
        }

    def pre_run(self):
        pass

    def run(self) -> EntryItem:
        with sync_playwright() as p:
            browser = self.launch_browser(p)
            page = browser.new_page()
            logger.info(f"Opening URL {self.url}...")
            page.goto(self.url, timeout=180_000)
            logger.info("Searching for ads...")
            page.locator(".tbl-feed-header-text").scroll_into_view_if_needed()
            page.locator("#boxComentarios").scroll_into_view_if_needed()

            entry_screenshot_path = self.take_screenshot(page, self.url, goto=False)
            entry_title = page.locator("title").inner_text()

            elements = page.locator(".videoCube")
            ad_items = []
            visible_elements = []
            for i in range(elements.count()):
                element = elements.nth(i)
                if not element.is_visible():
                    continue
                visible_elements.append(element)
                content = element.inner_html()
                ad_item = self.find_items(content)
                ad_items.append(ad_item)

            return EntryItem(
                title=entry_title,
                ads=ad_items,
                url=self.url,
                screenshot_path=entry_screenshot_path,
            )

import time

from playwright.sync_api import sync_playwright

from plays.base import BasePlay
from plays.items import AdItem, EntryItem
from plays.utils import get_or_none
from plog import logger


class UOLPlay(BasePlay):
    name = "uol"
    n_expected_ads = 4

    @classmethod
    def match(cls, url):
        # TODO: use regex in this matcher
        for domain in [
            "noticias.uol.com.br",
            "www.uol.com.br",
            "educacao.uol.com.br",
            "economia.uol.com.br",
        ]:
            if domain in url:
                return True

        return False

    def pre_run(self):
        pass

    def find_items(self, html_content) -> AdItem:
        return AdItem(
            title=get_or_none(r'<div class="ad-description">(.*?)</div>', html_content),
            url=get_or_none(
                r'link: {\s*[^}]*\bdefault\b[^}].*?"([^"]+)"',
                html_content
            ),
            thumbnail_url=get_or_none(
                r'image: {\s*default: "(https://tpc\.googlesyndication\.com/simgad/[\d?]+)"',
                html_content,
            ),
            tag=get_or_none(r'<div class="ad-label-footer">(.*?)</div>', html_content),
        )

    def get_iframe_items(self, iframe_object):
        iframe_object.scroll_into_view_if_needed()
        time.sleep(self.wait_time)
        frame_content = str(iframe_object.element_handles()[0].content_frame())
        return self.find_items(frame_content)

    def get_most_read_items(self, page_locator):
        page_items = page_locator.locator(".solar-headline")
        n_items = page_items.count()
        items = []
        for i in range(n_items):
            item = page_items.nth(i)
            html_content = item.inner_html()
            items.append(
                AdItem(
                    url=get_or_none(r'<a href="(.*?)"', html_content),
                    title=get_or_none(r'aria-label="(.*?)"', html_content),
                    thumbnail_url=get_or_none(r'source srcset="(.*?)"', html_content),
                    tag=None,
                )
            )

        return items

    def run(self) -> EntryItem:
        with sync_playwright() as p:
            browser = self.launch_browser(p)
            page = browser.new_page()
            logger.info(f"[{self.name}] Opening URL '{self.url}'...")
            page.goto(self.url, timeout=60_000)
            logger.info(f"[{self.name}] Searching for ads...")
            page.get_by_text("As mais lidas agora").scroll_into_view_if_needed()
            time.sleep(self.wait_time)
            ad_items = self.get_iframe_items(
                page.locator(".type-main").locator("//iframe")
            )
            most_read_items = self.get_most_read_items(page.locator(".jupiter-most-read-now"))

            entry_screenshot_path = self.take_screenshot(page, self.url, goto=False)

            entry_title = page.locator("h1.title").inner_text()
            all_items = [ad_items] + most_read_items

        return EntryItem(
            title=entry_title,
            ads=all_items,
            url=self.url,
            screenshot_path=entry_screenshot_path,
        )

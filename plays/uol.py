import time

from loguru import logger
from playwright.sync_api import sync_playwright

from plays.base import BasePlay
from plays.utils import get_or_none


class UOLPlay(BasePlay):
    def pre_run(self):
        pass

    def find_items(self, html_content):
        return {
            "thumbnail_url": get_or_none(
                r'image: {\s*default: "(https://tpc\.googlesyndication\.com/simgad/[\d?]+)"',
                html_content,
            ),
            "ad_title": get_or_none(r'<div class="ad-description">(.*?)</div>', html_content),
            "tag": get_or_none(r'<div class="ad-label-footer">(.*?)</div>', html_content),
            "ad_url": get_or_none(
                r'link: {\s*[^}]*\bdefault\b[^}].*?"([^"]+)"',
                html_content
            ),
        }

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
                {
                    "ad_url": get_or_none(r'<a href="(.*?)"', html_content),
                    "ad_title": get_or_none(r'aria-label="(.*?)"', html_content),
                    "thumbnail_url": get_or_none(r'source srcset="(.*?)"', html_content),
                    "ad_tag": None,
                }
            )

        return items

    def run(self):
        with sync_playwright() as p:
            logger.info("Launching Browser...")
            browser = p.firefox.launch(headless=self.headless)
            logger.info("Done!")
            page = browser.new_page()
            logger.info(f"Opening URL '{self.url}'...")
            page.goto(self.url, timeout=60_000)
            page.get_by_text("As mais lidas agora").scroll_into_view_if_needed()
            time.sleep(self.wait_time)
            ad_items = self.get_iframe_items(
                page.locator("[id^='google_ads_iframe_\\/8804\\/uol'][id$='_8']")
            )
            most_read_items = self.get_most_read_items(page.locator(".jupiter-most-read-now"))
            entry_title = page.locator("h1.title").inner_text()
            all_items = [ad_items] + most_read_items
            return {"entry_title": entry_title, "ad_items": all_items, "entry_url": self.url}
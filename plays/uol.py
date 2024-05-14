import time

from loguru import logger
from playwright.sync_api import sync_playwright

from plays.base import BasePlay
from plays.utils import get_or_none


class UOLPlay(BasePlay):
    def get_iframe_suffix(self):
        return get_or_none(r"www.uol.com.br/(\w+)/", self.url) or "noticias"

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

    def run(self):
        with sync_playwright() as p:
            logger.info("Launching Browser...")
            browser = p.firefox.launch(headless=self.headless)
            logger.info("Done!")
            page = browser.new_page()
            logger.info(f"Opening URL {self.url}...")
            page.goto(self.url, timeout=60_000)
            page.get_by_text("As mais lidas agora").scroll_into_view_if_needed()
            time.sleep(self.wait_time)
            iframe_suffix = self.get_iframe_suffix()
            iframe = page.locator(f"#google_ads_iframe_\\/8804\\/uol\\/{iframe_suffix}_8")
            page.locator("//iframe[@title='3rd party ad content']")
            iframe.scroll_into_view_if_needed()
            time.sleep(self.wait_time)
            frame_content = str(iframe.element_handles()[0].content_frame())
            items = self.find_items(frame_content)
            return items

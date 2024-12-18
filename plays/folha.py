import time

from decouple import config
from playwright.sync_api import TimeoutError as PlayWrightTimeoutError, sync_playwright

from plays.base import BasePlay
from plays.items import AdItem, EntryItem
from plays.utils import get_or_none
from plog import logger


class FolhaPlay(BasePlay):
    name = "folha"
    n_expected_ads = 12

    @classmethod
    def match(cls, url):
        return "folha.uol.com.br" in url

    def login(self):
        with sync_playwright() as p:
            browser = self.launch_browser(p)
            page = browser.new_page()
            login_url = "https://login.folha.com.br/login"
            logger.info(f"Opening URL {login_url}...")
            page.goto(login_url)
            time.sleep(self.wait_time)
            logger.info(f"Logging in into '{login_url}'...")
            page.locator("#registerEmail").fill(config("FOLHA_USERNAME"))
            page.locator("#registerPassword").fill(config("FOLHA_PASSWORD"))
            page.get_by_role("button", name="Entrar").click()
            time.sleep(self.wait_time)
            page.get_by_role("link", name="Entrar", exact=True).click()
            time.sleep(self.wait_time)
            logger.info("Login finished")
            logger.info("Closing browser")
            browser.close()

    def find_items(self, html_content) -> AdItem:
        return AdItem(
            title=get_or_none(r'title="(.*?)"', html_content),
            url=get_or_none(r'href="(.*?)"', html_content),
            thumbnail_url=get_or_none(r'url\(&quot;(.*?)&quot;\)', html_content),
            tag=get_or_none(r'<span class="branding-inner".*?>(.*?)<\/span>', html_content),
        )

    def pre_run(self):
        try:
            self.login()
        except PlayWrightTimeoutError:
            logger.warning("Timeout trying to log in. Probably already logged in")

    def run(self) -> EntryItem:
        with sync_playwright() as p:
            browser = self.launch_browser(p)
            page = browser.new_page()
            logger.info(f"[{self.name}] Opening URL '{self.url}'...")
            page.goto(self.url)
            logger.info(f"[{self.name}] Searching for ads...")
            time.sleep(self.wait_time)
            entry_title = page.locator(".c-content-head__title").inner_text()
            page.locator(".tbl-feed-header-text").scroll_into_view_if_needed()
            time.sleep(self.wait_time)

            elements = page.locator(".videoCube.syndicatedItem")

            entry_screenshot_path = self.take_screenshot(page, self.url, goto=False)

            n_elements = elements.count()
            ad_items = []
            for i in range(n_elements):
                element = elements.nth(i)
                if not element.is_visible():
                    continue
                object_raw_html = elements.nth(i).inner_html()
                ad_items.append(self.find_items(object_raw_html))

            logger.info("Done")

        return EntryItem(
            title=entry_title,
            ads=ad_items,
            url=self.url,
            screenshot_path=entry_screenshot_path,
        )

import time

from decouple import config
from playwright.sync_api import TimeoutError as PlayWrightTimeoutError, sync_playwright

from plays.base import BasePlay
from plays.items import AdItem, EntryItem
from plays.utils import get_or_none
from plog import logger


class GloboPlay(BasePlay):
    name = "globo"
    n_expected_ads = 50
    kwargs = {"allow_remove_session": False}

    def login(self):
        with sync_playwright() as p:
            browser = self.launch_browser(p)
            page = browser.new_page()
            login_url = "https://login.globo.com/login/"
            logger.info(f"Opening URL {login_url}...")
            page.goto(login_url)
            time.sleep(self.wait_time)
            page.locator("#barra-item-login").click()
            page.locator("#login").fill(config("GLOBO_USERNAME"))
            page.locator("#password").fill(config("GLOBO_PASSWORD"))
            page.locator("#login-button").click()

    @classmethod
    def match(cls, url):
        return "oglobo.globo.com/" in url

    def find_items(self, html_content) -> AdItem:
        return AdItem(
            title=get_or_none(r'title="(.*?)"', html_content),
            url=get_or_none(r'href="(.*?)"', html_content),
            thumbnail_url=get_or_none(r'url\(&quot;(.*?)&quot;\)', html_content),
            tag=get_or_none(r'<span class="branding-inner".*?>(.*?)<\/span>', html_content),
            excerpt=get_or_none(r'slot="description" title="(.*?)"', html_content),
        )

    def pre_run(self):
        pass

    def is_logged_in(self, page):
        try:
            page.locator(".login-profile__menu").first.inner_html()
        except PlayWrightTimeoutError:
            raise Exception(f"[{self.name}] Not logged in!")

    def run(self) -> EntryItem:
        with sync_playwright() as p:
            browser = self.launch_browser(p)
            page = browser.new_page()
            logger.info(f"[{self.name}] Opening URL '{self.url}'...")
            page.goto(self.url, timeout=180_000)
            logger.info(f"[{self.name}] Searching for ads...")

            self.is_logged_in(page)

            page.locator(".tbl-feed-header-text").scroll_into_view_if_needed()
            self.scroll_down(page, 40, 400, wait_time=1)
            page.locator("#boxComentarios").scroll_into_view_if_needed()

            entry_screenshot_path = self.take_screenshot(page, self.url, goto=False, timeout=60_000)
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

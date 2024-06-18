import time

from decouple import config
from playwright.sync_api import TimeoutError as PlayWrightTimeoutError, sync_playwright

from plays.base import BasePlay
from plays.items import AdItem, EntryItem
from plays.utils import get_or_none
from plog import logger


class EstadaoPlay(BasePlay):
    name = "estadao"
    n_expected_ads = 9

    @classmethod
    def match(cls, url):
        return "estadao.com.br" in url

    def login(self):
        with sync_playwright() as p:
            browser = self.launch_browser(p)
            logger.info("Done!")
            page = browser.new_page()
            url = "https://acesso.estadao.com.br/login/"
            logger.info(f"Opening URL {url}...")
            page.goto(url)
            time.sleep(self.wait_time)
            logger.info(f"Logging in into {url}...")
            page.locator("#email_login").fill(config("ESTADAO_USERNAME"))
            page.locator("#senha").fill(config("ESTADAO_PASSWORD"))
            page.get_by_role("button", name="Entrar").click()
            time.sleep(self.wait_time)
            logger.info("Login finished")
            logger.info("Closing browser")
            browser.close()

    def pre_run(self):
        try:
            self.login()
        except PlayWrightTimeoutError:
            logger.warning("Timeout trying to log in. Probably already logged in")

    def get_objects(self, elements):
        n_elements = elements.count()
        objects = []
        elements_row = []
        for i in range(n_elements):
            current_element = elements.nth(i)
            elements_row.append(current_element)
            objects.append(current_element.inner_html())

        return objects

    def find_items(self, html_content) -> AdItem:
        return AdItem(
            title=get_or_none(r'title="(.*?)"', html_content),
            url=get_or_none(r'href="(.*?)"', html_content),
            thumbnail_url=get_or_none(r'src="(.*?)"', html_content),
            tag=get_or_none(
                r'<span class="ob-unit ob-rec-source" data-type="Source">(.*?)<\/span>',
                html_content
            ),
        )

    def run(self) -> EntryItem:
        with sync_playwright() as p:
            browser = self.launch_browser(p)
            page = browser.new_page()
            logger.info(f"[{self.name}] Opening URL '{self.url}'...")
            page.goto(self.url)
            time.sleep(self.wait_time)
            logger.info(f"[{self.name}] Searching for ads...")
            page.locator(".OB-REACT-WRAPPER").scroll_into_view_if_needed()
            time.sleep(self.wait_time)
            page.locator("//footer").first.scroll_into_view_if_needed()
            elements = page.locator(".ob-dynamic-rec-container")
            time.sleep(self.wait_time * 2)

            entry_screenshot_path = self.take_screenshot(page, self.url, goto=False)

            objects = self.get_objects(elements)
            ad_items = []
            entry_title = page.locator("h1").first.inner_text()
            for obj in objects:
                ad_items.append(self.find_items(obj))

        return EntryItem(
            title=entry_title,
            url=self.url,
            screenshot_path=entry_screenshot_path,
            ads=ad_items,
        )

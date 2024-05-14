import time

from decouple import config
from loguru import logger
from playwright.sync_api import TimeoutError as PlayWrightTimeoutError, sync_playwright

from plays.base import BasePlay
from plays.utils import get_or_none


class EstadaoPlay(BasePlay):
    def login(self):
        with sync_playwright() as p:
            logger.info("Launching Browser...")
            browser = p.firefox.launch_persistent_context(self.session_dir, headless=self.headless)
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
        logger.info(f"Found {n_elements} elements")
        objects = []
        elements_row = []
        for i in range(n_elements):
            current_element = elements.nth(i)
            elements_row.append(current_element)
            objects.append(current_element.inner_html())

        return objects

    def find_items(self, html_content):
        return {
            "ad_title": get_or_none(r'title="(.*?)"', html_content),
            "ad_url": get_or_none(r'href="(.*?)"', html_content),
            "thumbnail_url": get_or_none(r'src="(.*?)"', html_content),
            "tag": get_or_none(
                r'<span class="ob-unit ob-rec-source" data-type="Source">(.*?)<\/span>',
                html_content
            ),
        }

    def run(self):
        with sync_playwright() as p:
            logger.info("Launching Browser...")
            browser = p.firefox.launch_persistent_context(
                self.session_dir,
                headless=self.headless
            )
            logger.info("Done!")
            page = browser.new_page()
            logger.info(f"Opening URL '{self.url}'...")
            page.goto(self.url)
            time.sleep(self.wait_time)
            page.locator(".OB-REACT-WRAPPER").scroll_into_view_if_needed()
            time.sleep(self.wait_time)
            page.locator("//footer").first.scroll_into_view_if_needed()
            elements = page.locator(".ob-dynamic-rec-container")
            time.sleep(self.wait_time)
            objects = self.get_objects(elements)
            ad_items = []
            entry_title = page.locator("h1").first.inner_text()
            for obj in objects:
                ad_items.append(self.find_items(obj))

        return {"entry_title": entry_title, "ad_items": ad_items, "entry_url": self.url}

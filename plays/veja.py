import time

from loguru import logger
from playwright.sync_api import TimeoutError as PlaywirghtTimeoutError, sync_playwright

from plays.base import BasePlay
from plays.utils import get_or_none


class VejaPlay(BasePlay):
    def find_items(self, html_content, ad_panel_content, thumbnail_content):
        return {
            "ad_title": get_or_none(r"<title>(.*?)</title>", html_content),
            "ad_url": get_or_none(r'</script>\n<a href="(.*?)"', html_content),
            "thumbnail_url": get_or_none(r'img src="(.*?)"', thumbnail_content),
            "tag": get_or_none(
                r'<div class="mcdomain"><a[^>]+>(.*?)<\/a><\/div>',
                ad_panel_content
            ),
        }

    def parse_elements(self, elements):
        n_elements = elements.count()
        elements_row = []
        for i in range(n_elements):
            current_element = elements.nth(i)
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
            except PlaywirghtTimeoutError:
                logger.error(f"Error getting href from {ele}")

        return hrefs

    def pre_run(self):
        pass

    def run(self):
        with sync_playwright() as p:
            browser = p.firefox.launch_persistent_context(self.session_dir, headless=self.headless)
            page = browser.new_page()
            logger.info(f"Opening URL '{self.url}'...")
            page.goto(self.url)
            logger.info("Searching for ads...")
            time.sleep(self.wait_time)
            page.locator(".mgbox").scroll_into_view_if_needed()
            time.sleep(self.wait_time)

            entry_title = page.locator("h1.title").inner_text()

            elements = page.locator(".mgline")

            elements = self.parse_elements(elements)
            hrefs = self.get_hrefs(elements)
            page = browser.new_page()
            ad_items = []
            for element, href in zip(elements, hrefs):
                try:
                    logger.info(f"Opening AD URL '{href}'")
                    page.goto(href)
                    time.sleep(self.wait_time)
                    logger.info(f"Getting page content '{href}'")
                    page_content = page.content()
                    thumbnail_content = page.locator(".news__image_big").inner_html()
                    element_content = element.inner_html()
                    ad_items.append(
                        self.find_items(page_content, element_content, thumbnail_content)
                    )
                except PlaywirghtTimeoutError:
                    logger.error(f"Error getting content from '{href}'")

            logger.info("Done")
            return {"entry_title": entry_title, "ad_items": ad_items, "entry_url": self.url}
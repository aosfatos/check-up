import time

from playwright.sync_api import sync_playwright

from plays.base import BasePlay
from plays.items import AdItem, EntryItem
from plays.utils import get_or_none
from plog import logger


class MetropolesPlay(BasePlay):
    name = "metropoles"
    n_expected_ads = 10

    @classmethod
    def match(cls, url):
        return "metropoles.com" in url

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

    def run(self) -> EntryItem:
        with sync_playwright() as p:
            browser = self.launch_browser(p, viewport={"width": 1920, "height": 1080})
            page = browser.new_page()
            logger.info(f"[{self.name}] Opening URL '{self.url}'...")
            page.goto(self.url, timeout=180_000)
            logger.info(f"[{self.name}] Searching for ads...")
            try:
                page.locator("#taboola-below-article-thumbnails").scroll_into_view_if_needed()
            except Exception:
                logger.warning(
                    f"[{self.name}] Timeout error waiting for 'taboola-below-article-thumbnails'"
                )
            time.sleep(self.wait_time * 2)

            entry_screenshot_path = self.take_screenshot(page, self.url, goto=False)
            entry_title = page.locator("//h1").first.inner_text()

            self.scroll_down(page, 20, amount=500)

            elements = page.locator(".videoCube")
            ad_items = []
            visible_elements = []
            time.sleep(self.wait_time)
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

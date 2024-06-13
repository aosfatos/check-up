import shutil
import time
from tempfile import NamedTemporaryFile
from typing import List

from playwright.sync_api import TimeoutError as PlayWrightTimeoutError, sync_playwright

from plays.items import AdItem, EntryItem
from plays.timeout import PlayTimeout, PlayerTimeoutError
from plays.exceptions import NotEnoughADSFound, ScraperNotFoundError
from plog import logger


class BasePlay:
    name = "base"
    n_expected_ads = 0

    def __init__(
        self,
        url,
        session_dir=None,
        proxy=None,
        wait_time=3,
        headless=True,
        retries=3,
        allow_remove_session=True,
        timeout_seconds=600,
    ):
        self.url = url
        self.session_dir = session_dir
        self.proxy = proxy
        self.wait_time = wait_time
        self.headless = headless
        self.retries = retries
        self.allow_remove_session = allow_remove_session
        self.timeout_seconds = timeout_seconds

    @classmethod
    def match(cls, url):
        raise NotImplementedError()

    @classmethod
    def extra_kwargs(cls):
        return dict()

    @classmethod
    def get_scraper(cls, url, *args, **kwargs):
        scrapers = cls.__subclasses__()
        for scraper in scrapers:
            if scraper.match(url):
                return scraper(url, *args, **scraper.extra_kwargs())

        raise ScraperNotFoundError(f"No scraper was found for url '{url}'")

    def get_session_dir(self):
        if self.session_dir is None:
            return f"./sessions/{self.name}_session/"

        return self.session_dir

    def take_screenshot(self, page, url, goto=True, timeout=30_000):
        logger.info(f"[{self.name}] Taking screenshot of '{url}'...")
        temp_file = NamedTemporaryFile(suffix=".png", delete=False)
        if goto:
            page.goto(url)
        page.screenshot(full_page=True, path=temp_file.name, timeout=timeout)
        logger.info("Done!")
        return temp_file.name

    def scroll_down(self, page, n, amount=300, wait_time=1):
        for _ in range(n):
            page.mouse.wheel(0, amount)
            time.sleep(wait_time)

    def launch_browser(self, playwright_obj, use_proxy=True, *args, **kwargs):
        logger.info(f"[{self.name}] Launching browser...'")
        if self.proxy is not None and use_proxy:
            logger.info(f"[{self.name}] Using proxy")
            return playwright_obj.firefox.launch_persistent_context(
                self.get_session_dir(),
                headless=self.headless,
                proxy=self.proxy,
                *args,
                **kwargs,
            )
        return playwright_obj.firefox.launch_persistent_context(
            self.get_session_dir(),
            headless=self.headless,
            *args,
            **kwargs,
        )

    def take_ads_screenshot(self, ad_items: List[AdItem]):
        logger.info(f"[{self.name}] Taking ADs screenshots")
        with sync_playwright() as p:
            browser = self.launch_browser(p)
            page = browser.new_page()
            for ad in ad_items:
                try:
                    screenshot_path = self.take_screenshot(page, ad.url, goto=True)
                except Exception:
                    screenshot_path = None
                finally:
                    ad.screenshot_path = screenshot_path

        logger.info("Done!")
        return ad_items

    def remove_session(self):
        if self.allow_remove_session:
            try:
                logger.info(f"[{self.name}] Removing session...")
                shutil.rmtree(self.get_session_dir())
                logger.info(f"[{self.name}] Done!")
            except Exception:
                logger.error(
                    f"[{self.name}] Error deleting session dir: '{self.get_session_dir()}'"
                )

        else:
            logger.info(f"[{self.name}] Removing session not allowed...")

    def not_enough_items(self, entry_item: EntryItem):
        return entry_item is None or len(entry_item.ads) < self.n_expected_ads

    def pre_run(self):
        raise NotImplementedError()

    def post_run(self, output):
        return output

    def run(self):
        raise NotImplementedError()

    def execute(self, retries=2):
        entry_item = None
        self.pre_run()
        while self.not_enough_items(entry_item) and retries >= 0:
            try:
                with PlayTimeout(seconds=self.timeout_seconds, name=self.name):
                    entry_item = self.run()
                logger.info(f"[{self.name}]: Found {len(entry_item.ads)} items.")
            except PlayWrightTimeoutError as exc:
                logger.error(str(exc))
            except PlayerTimeoutError as exc:
                logger.error(str(exc))

            if self.not_enough_items(entry_item):
                logger.warning(
                    f"[{self.name}] Not enough ADs were found with '{self.name}'."
                    f" Trying again. Remaining {retries}"
                )
                # Remove session and login again. It sometimes work
                self.remove_session()
                retries -= 1

        if self.not_enough_items(entry_item):
            raise NotEnoughADSFound(f"[{self.name}] Not enough ads were found in '{self.url}'")

        entry_item = self.post_run(entry_item)
        if entry_item is not None:
            entry_item.ads = self.take_ads_screenshot(entry_item.ads)
        return entry_item

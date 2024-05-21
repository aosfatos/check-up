import shutil
from tempfile import NamedTemporaryFile

from loguru import logger
from playwright.sync_api import TimeoutError as PlayWrightTimeoutError, sync_playwright

from plays.exceptions import ScrapperNotFoundError


class BasePlay:
    name = "base"
    n_expected_ads = 0

    def __init__(self, url, session_dir=None, wait_time=3, headless=True, retries=3):
        self.url = url
        self.session_dir = session_dir
        self.wait_time = wait_time
        self.headless = headless
        self.retries = retries

    @classmethod
    def match(cls, url):
        raise NotImplementedError()

    @classmethod
    def get_scrapper(cls, url, *args, **kwargs):
        from plays import EstadaoPlay, FolhaPlay, VejaPlay, UOLPlay

        scrappers = [EstadaoPlay, FolhaPlay, VejaPlay, UOLPlay]
        for scrapper in scrappers:
            if scrapper.match(url):
                return scrapper(url, *args, **kwargs)

        raise ScrapperNotFoundError(f"No scrapper was found for url '{url}'")

    @property
    def proxy(self):
        return None

    def get_session_dir(self):
        if self.session_dir is None:
            return f"/tmp/{self.name}_session"

        return self.session_dir

    def take_screenshot(self, page, url, goto=True):
        logger.info(f"Taking screenshot from {url}...")
        temp_file = NamedTemporaryFile(suffix=".png", delete=False)
        if goto:
            page.goto(url)
        page.screenshot(full_page=True, path=temp_file.name)
        logger.info("Done!")
        return temp_file.name

    def launch_browser(self, playwright_obj):
        logger.info(f"[{self.name}] Launching browser...'")
        if self.proxy is not None:
            return playwright_obj.firefox.launch_persistent_context(
                self.get_session_dir(),
                headless=self.headless,
                proxy=self.proxy,
            )
        return playwright_obj.firefox.launch_persistent_context(
            self.get_session_dir(),
            headless=self.headless
        )

    def take_ads_screenshot(self, ad_items):
        logger.info(f"[{self.name}] Taking ADs screenshots")
        with sync_playwright() as p:
            browser = self.launch_browser(p)
            page = browser.new_page()
            for ad in ad_items:
                try:
                    screenshot_path = self.take_screenshot(page, ad["ad_url"], goto=True)
                except Exception:
                    screenshot_path = None
                finally:
                    ad["screenshot_path"] = screenshot_path

        logger.info("Done!")
        return ad_items

    def remove_session(self):
        try:
            shutil.rmtree(self.get_session_dir())
        except Exception:
            logger.error(f"[{self.name}] Error deleting session dir: '{self.session_dir}'")

    def not_enough_items(self, output):
        return output is None or len(output["ad_items"]) < self.n_expected_ads

    def pre_run(self):
        raise NotImplementedError()

    def post_run(self, output):
        return output

    def run(self):
        raise NotImplementedError()

    def execute(self, retries=2):
        output = None
        self.pre_run()
        # TODO: retry
        while self.not_enough_items(output) and retries > 0:
            try:
                output = self.run()
                logger.info(f"{self.name.capitalize()}: found {len(output['ad_items'])} items.")
            except PlayWrightTimeoutError as exc:
                logger.error(str(exc))

            if self.not_enough_items(output):
                retries -= 1
                logger.warning(
                    f"[{self.name}] Not enough ADs were found with '{self.name}'."
                    f" Trying again. Remaining {retries}"
                )
                # Lets remove session and login again. It sometimes works
                self.remove_session()

        output = self.post_run(output)
        if output is not None:
            output["ad_items"] = self.take_ads_screenshot(output["ad_items"])
        return output

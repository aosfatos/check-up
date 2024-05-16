from tempfile import NamedTemporaryFile

from loguru import logger
from playwright.sync_api import TimeoutError as PlayWrightTimeoutError, sync_playwright

from plays.exceptions import ScrapperNotFoundError


class BasePlay:
    name = "base"

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

    def take_ads_screenshot(self, ad_items):
        logger.info("Taking ADs screenshots")
        with sync_playwright() as p:
            browser = p.firefox.launch_persistent_context(
                self.get_session_dir(),
                headless=self.headless
            )
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

    def pre_run(self):
        raise NotImplementedError()

    def post_run(self, output):
        return output

    def run(self):
        raise NotImplementedError()

    def execute(self):
        output = None
        self.pre_run()
        # TODO: retry
        try:
            output = self.run()
            logger.info(f"{self.name.capitalize()}: found {len(output['ad_items'])} items.")
        except PlayWrightTimeoutError as exc:
            logger.error(str(exc))

        output = self.post_run(output)
        if output is not None:
            output["ad_items"] = self.take_ads_screenshot(output["ad_items"])
        return output

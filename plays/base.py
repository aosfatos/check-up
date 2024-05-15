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

    def take_screenshot(self, page, url):
        temp_file = NamedTemporaryFile(suffix=".png", delete=False)
        page.goto(url)
        page.screenshot(full_page=True, path=temp_file.name)
        return temp_file.name

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
        logger.info(f"Taking screenshots of {output['entry_url']}...")
        with sync_playwright() as p:
            browser = p.firefox.launch_persistent_context(
                self.get_session_dir(),
                headless=self.headless
            )
            page = browser.new_page()
            output["entry_screenshot_path"] = self.take_screenshot(page, output["entry_url"])
            for ad_item in output["ad_items"]:
                logger.info(f"Taking screenshots of {ad_item['ad_url']}...")
                ad_item["screenshot_path"] = self.take_screenshot(page, ad_item["ad_url"])
        return output

from loguru import logger
from playwright.sync_api import TimeoutError as PlayWrightTimeoutError

from plays.exceptions import ScrapperNotFoundError


class BasePlay:
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
        except PlayWrightTimeoutError as exc:
            logger.error(str(exc))

        output = self.post_run(output)
        return output

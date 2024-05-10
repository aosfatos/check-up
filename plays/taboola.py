import time
from pathlib import Path
from uuid import uuid4

from loguru import logger
from playwright.sync_api import sync_playwright


PERSISTENT_DIR = Path("./persistent")
WAIT_TIME = 3


def crawl_taboola(url, screenshot=False):
    with sync_playwright() as p:
        browser = p.firefox.launch_persistent_context(PERSISTENT_DIR)
        page = browser.new_page()
        logger.info(f"Opening URL {url}...")
        page.goto(url)
        logger.info("Searching for ads...")
        time.sleep(WAIT_TIME)
        page.locator(".tbl-feed-header-text").scroll_into_view_if_needed()
        time.sleep(WAIT_TIME)
        time.sleep(WAIT_TIME)
        if screenshot:
            screenshot_name = str(uuid4())
            logger.info(f"Taking screenshot from {url}. Saving file at {screenshot_name}")
            page.screenshot(path=f"/tmp/{screenshot_name}.png", full_page=True, timeout=20_000)

        elements = page.locator(".videoCube")
        n_elements = elements.count()
        objects = []
        for i in range(n_elements):
            objects.append(elements.nth(i).inner_html())

        logger.info("Done")

    return objects

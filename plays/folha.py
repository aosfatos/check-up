import time
from pathlib import Path
from uuid import uuid4

from decouple import config
from loguru import logger
from playwright.sync_api import sync_playwright


PERSISTENT_DIR = Path("./persistent")
WAIT_TIME = 3


def login():
    with sync_playwright() as p:
        logger.info("Launching Browser...")
        browser = p.firefox.launch_persistent_context(PERSISTENT_DIR)
        logger.info("Done!")
        page = browser.new_page()
        url = "https://login.folha.com.br/login"
        logger.info(f"Opening URL {url}...")
        page.goto(url)
        time.sleep(WAIT_TIME)
        logger.info(f"Logging in into {url}...")
        page.locator("#registerEmail").fill(config("FOLHA_USERNAME"))
        page.locator("#registerPassword").fill(config("FOLHA_PASSWORD"))
        page.get_by_role("button", name="Entrar").click()
        time.sleep(WAIT_TIME)
        page.get_by_role("link", name="Entrar", exact=True).click()
        time.sleep(WAIT_TIME)
        logger.info("Login finished")
        logger.info("Closing browser")
        browser.close()


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

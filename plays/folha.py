import time
from pathlib import Path

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

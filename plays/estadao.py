import time
from pathlib import Path

from decouple import config
from loguru import logger
from playwright.sync_api import sync_playwright


PERSISTENT_DIR = Path("./estadao-session")
WAIT_TIME = 3
HEADLESS = config("HEADLESS", cast=bool)


def get_objects(elements):
    n_elements = elements.count()
    logger.info(f"Found {n_elements} elements")
    objects = []
    elements_row = []
    for i in range(n_elements):
        current_element = elements.nth(i)
        elements_row.append(current_element)
        objects.append(current_element.inner_html())

    return objects


def login():
    with sync_playwright() as p:
        logger.info("Launching Browser...")
        browser = p.firefox.launch_persistent_context(PERSISTENT_DIR, headless=HEADLESS)
        logger.info("Done!")
        page = browser.new_page()
        url = "https://acesso.estadao.com.br/login/"
        logger.info(f"Opening URL {url}...")
        page.goto(url)
        time.sleep(WAIT_TIME)
        logger.info(f"Logging in into {url}...")
        page.locator("#email_login").fill(config("ESTADAO_USERNAME"))
        page.locator("#senha").fill(config("ESTADAO_PASSWORD"))
        page.get_by_role("button", name="Entrar").click()
        time.sleep(WAIT_TIME)
        logger.info("Login finished")
        logger.info("Closing browser")
        browser.close()


def outbrain(url):
    with sync_playwright() as p:
        logger.info("Launching Browser...")
        browser = p.firefox.launch_persistent_context(PERSISTENT_DIR, headless=HEADLESS)
        logger.info("Done!")
        page = browser.new_page()
        logger.info(f"Opening URL '{url}'...")
        page.goto(url)
        time.sleep(WAIT_TIME)
        page.locator(".OB-REACT-WRAPPER").scroll_into_view_if_needed()
        time.sleep(WAIT_TIME)
        elements = page.locator(".ob-dynamic-rec-container")
        return get_objects(elements)

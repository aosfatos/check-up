import time

from decouple import config
from loguru import logger
from pathlib import Path
from playwright.sync_api import TimeoutError as PlaywirghtTimeoutError, sync_playwright


WAIT_TIME = 3
PERSISTENT_DIR = Path("./veja-session")
HEADLESS = config("HEADLESS", cast=bool)


def get_objects(elements):
    n_elements = elements.count()
    objects = []
    elements_row = []
    for i in range(n_elements):
        current_element = elements.nth(i)
        elements_row.append(current_element)
        objects.append(current_element.inner_html())

    return objects, elements_row


def get_hrefs(elements):
    hrefs = []
    for ele in elements:
        try:
            logger.info(f"Getting href attribute from '{ele}'")
            href = ele.locator("a").first.get_attribute("href")
            logger.info(f"Got '{href}'")
            hrefs.append(href)
        except PlaywirghtTimeoutError:
            logger.error(f"Error getting href from {ele}")

    return hrefs


def crawl_mgid(url):
    with sync_playwright() as p:
        browser = p.firefox.launch_persistent_context(PERSISTENT_DIR, headless=HEADLESS)
        page = browser.new_page()
        logger.info(f"Opening URL {url}...")
        page.goto(url, timeout=60_000)
        logger.info("Searching for ads...")
        time.sleep(WAIT_TIME)
        page.locator(".mgbox").scroll_into_view_if_needed()
        time.sleep(WAIT_TIME)

        elements = page.locator(".mgline")

        objs, elements = get_objects(elements)
        hrefs = get_hrefs(elements)
        ad_pages = []
        for href in hrefs:
            try:
                logger.info(f"Opening AD URL '{href}'")
                page.goto(href)
                time.sleep(WAIT_TIME * 2)
                logger.info(f"Getting page content '{href}'")
                ad_pages.append(page.content())
            except PlaywirghtTimeoutError:
                logger.error(f"Error getting content from '{href}'")

        logger.info("Done")
        return objs, ad_pages

import time
from pathlib import Path

from decouple import config
from loguru import logger
from playwright.sync_api import sync_playwright

from plays.utils import get_or_none


PERSISTENT_DIR = Path("./folha-session")
WAIT_TIME = 3
HEADLESS = config("HEADLESS", cast=bool)


def find_attributes(html_content):
    return {
        "ad_title": get_or_none(r'title="(.*?)"', html_content),
        "ad_url": get_or_none(r'href="(.*?)"', html_content),
        "thumbnail_url": get_or_none(r'url\(&quot;(.*?)&quot;\)', html_content),
        "tag": get_or_none(r'<span class="branding-inner".*?>(.*?)<\/span>', html_content),
    }


def login():
    with sync_playwright() as p:
        logger.info("Launching Browser...")
        browser = p.firefox.launch_persistent_context(PERSISTENT_DIR, headless=HEADLESS)
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


def crawl_taboola(url):
    with sync_playwright() as p:
        browser = p.firefox.launch_persistent_context(PERSISTENT_DIR, headless=HEADLESS)
        page = browser.new_page()
        logger.info(f"Opening URL {url}...")
        page.goto(url)
        logger.info("Searching for ads...")
        time.sleep(WAIT_TIME)
        entry_title = page.locator(".c-content-head__title").inner_text()
        page.locator(".tbl-feed-header-text").scroll_into_view_if_needed()
        time.sleep(WAIT_TIME)

        elements = page.locator(".videoCube")
        n_elements = elements.count()
        ad_attributes = []
        for i in range(n_elements):
            object_raw_html = elements.nth(i).inner_html()
            ad_attributes.append(find_attributes(object_raw_html))

        logger.info("Done")

    return {"entry_title": entry_title, "ads": ad_attributes}

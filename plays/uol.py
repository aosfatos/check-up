import time

from decouple import config
from loguru import logger
from playwright.sync_api import sync_playwright

from plays.utils import get_or_none


HEADLESS = config("HEADLESS", cast=bool)
WAIT_TIME = 3


def find_items(html_content):
    return {
        "thumbnail_url": get_or_none(
            r'image: {\s*default: "(https://tpc\.googlesyndication\.com/simgad/[\d?]+)"',
            html_content,
        ),
        "ad_title": get_or_none(r'<div class="ad-description">(.*?)</div>', html_content),
        "tag": get_or_none(r'<div class="ad-label-footer">(.*?)</div>', html_content),
        "ad_url": get_or_none(
            r'link: {\s*[^}]*\bdefault\b[^}].*?"([^"]+)"',
            html_content
        ),
    }


def crawl_uol(url):
    with sync_playwright() as p:
        logger.info("Launching Browser...")
        browser = p.firefox.launch(headless=HEADLESS)
        logger.info("Done!")
        page = browser.new_page()
        page.goto(url, timeout=60_000)
        page.get_by_text("As mais lidas agora").scroll_into_view_if_needed()
        time.sleep(WAIT_TIME)
        iframe_suffix = get_or_none(r"www.uol.com.br/(\w+)/", url) or "noticias"
        iframe = page.locator(f"#google_ads_iframe_\\/8804\\/uol\\/{iframe_suffix}_8")
        page.locator("//iframe[@title='3rd party ad content']")
        iframe.scroll_into_view_if_needed()
        time.sleep(WAIT_TIME)
        iframe.screenshot(path="/tmp/iframe.png")
        frame_content = str(iframe.element_handles()[0].content_frame())
        items = find_items(frame_content)
        return items

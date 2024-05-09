import time

from decouple import config
from playwright.sync_api import sync_playwright


def login(page):
    url = "https://login.folha.com.br/login"
    page.goto(url)
    time.sleep(3)
    page.locator("#registerEmail").fill(config("FOLHA_USERNAME"))
    page.locator("#registerPassword").fill(config("FOLHA_PASSWORD"))
    page.get_by_role("button", name="Entrar").click()
    time.sleep(10)
    page.get_by_role("link", name="Entrar", exact=True).click()
    time.sleep(10)


def crawl_taboola(url, screenshot=False):
    with sync_playwright() as p:
        browser = p.firefox.launch_persistent_context("/tmp/persistent")
        page = browser.new_page()
        page.goto(url)
        time.sleep(10)
        page.locator(".tbl-feed-header-text").scroll_into_view_if_needed()
        time.sleep(10)
        time.sleep(3)
        # page.evaluate("window.scrollBy(0, document.body.scrollHeight);")
        # time.sleep(3)
        if screenshot:
            page.screenshot(path="/project/spiders/example.png", full_page=True, timeout=20_000)

        elements = page.locator(".videoCube")
        n_elements = elements.count()
        objects = []
        for i in range(n_elements):
            objects.append(elements.nth(i).inner_html())

    return objects

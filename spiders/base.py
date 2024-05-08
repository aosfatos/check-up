import scrapy


class BaseSpider(scrapy.Spider):
    name = "base"
    custom_settings = {
        "CLOSESPIDER_PAGECOUNT": 12,
        "TWISTED_REACTOR": "twisted.internet.asyncioreactor.AsyncioSelectorReactor",
        "DOWNLOAD_HANDLERS": {
            "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
            "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
        },
        "DEPTH_LIMIT": 1,
    }

    async def errback(self, failure):
        page = failure.request.meta["playwright_page"]
        await page.close()

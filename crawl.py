from scrapy.crawler import CrawlerProcess

from plog import logger
from spiders.base import BaseSpider

process = CrawlerProcess(
    settings={
        "ITEM_PIPELINES": {"pipelines.PostgresPipeline": 300},
    }
)


def run():
    for crawler_class in BaseSpider.__subclasses__():
        process.crawl(crawler_class)
    process.start()


if __name__ == "__main__":
    logger.info("Starting crawlers...")
    run()
    logger.info("Done!")

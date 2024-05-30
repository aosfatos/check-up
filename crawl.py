import sched
import time

from scrapy.crawler import CrawlerProcess

from spiders.base import BaseSpider


scheduler = sched.scheduler(time.time, time.sleep)

duration = 86_400  # every 24h


process = CrawlerProcess(
    settings={
        "ITEM_PIPELINES": {"pipelines.PostgresPipeline": 300},
    }
)


def event_loop():
    main()
    scheduler.enter(duration, 1, event_loop)


def run():
    event_loop()
    scheduler.run()


def main():
    for crawler_class in BaseSpider.__subclasses__():
        process.crawl(crawler_class)
        process.start()


if __name__ == "__main__":
    run()

from scrapy.crawler import CrawlerProcess

from spiders.folha import FolhaSpider


process = CrawlerProcess(
    settings={
        "ITEM_PIPELINES": {"pipelines.PostgresPipeline": 300},
    }
)

process.crawl(FolhaSpider)
process.start()

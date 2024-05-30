from decouple import config
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

# TODO move this model to scrapers and use reflection here
from models import URLQueue


class PostgresPipeline:
    def __init__(self):
        self.engine = create_engine(config("DATABASE_URL"))
        self.session = Session(self.engine)

    def process_item(self, item, spider):
        URLQueue.create(self.session, item["url"])
        return item

    def close_spider(self, spider):
        self.session.close()
        self.engine.dispose()

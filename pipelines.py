from decouple import config
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from models import URLQueue


class PostgresPipeline:
    def __init__(self):
        self.engine = create_engine(config("DATABASE_URL"))
        self.session = Session(self.engine)

    def process_item(self, item, spider):
        exists = self.session.query(URLQueue).filter(URLQueue.url == item["url"]).first()
        if exists is None:
            URLQueue.create(self.session, item["url"])

        return item

    def close_spider(self, spider):
        self.session.close()
        self.engine.dispose()

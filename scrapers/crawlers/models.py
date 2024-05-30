import datetime

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Boolean, Column, DateTime, Integer
from sqlalchemy_utils import URLType


Base = declarative_base()


class URLQueue(Base):
    __tablename__ = "urlqueue"

    id = Column(Integer, primary_key=True)
    url = Column(URLType, nullable=False)
    processed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    def __repr__(self):
        return f"{self.url}- {self.created_at}"

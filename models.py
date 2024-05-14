import datetime
from typing import List

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy_utils import URLType


Base = declarative_base()


class Portal(Base):
    __tablename__ = "portal"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name = Column(String, unique=True)
    url = Column(URLType, unique=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    entries: Mapped[List["Entry"]] = relationship(back_populates="portal")

    def __repr__(self):
        return f"{self.name} ({self.url})"


class Entry(Base):
    __tablename__ = "entry"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    portal_id: Mapped[int] = mapped_column(ForeignKey("portal.id"))
    title = Column(String, nullable=False)
    url = Column(URLType, unique=True, nullable=False)
    screenshot = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    portal: Mapped["Portal"] = relationship(back_populates="entries")
    ads: Mapped[List["Advertisement"]] = relationship(back_populates="entry")

    def __repr__(self):
        return f"{self.portal.name}: {self.url} - ({self.created_at})"


class Advertisement(Base):
    __tablename__ = "advertisement"

    id = Column(Integer, primary_key=True)
    entry_id: Mapped[int] = mapped_column(ForeignKey("entry.id"))
    url = Column(URLType, unique=True, nullable=False)
    title = Column(String, nullable=False)
    tag = Column(String, nullable=True)
    thumbnail_url = Column(URLType, nullable=False)
    screenshot = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    entry: Mapped["Entry"] = relationship(back_populates="ads")

    def __repr__(self):
        return f"{self.url}: ({self.entry.url})"

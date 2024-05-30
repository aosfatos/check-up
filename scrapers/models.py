import datetime
from contextlib import suppress
from typing import List

from slugify import slugify
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

from download import dowload_media
from utils.date import now, folder_date
from storage import upload_file


Base = declarative_base()


def get_or_create_portal(session, portal_id):
    post = session.query(Portal).filter_by(id=portal_id).first()
    if post:
        created = False
        return post, created
    else:
        created = True
        post = Portal(id=portal_id)
        session.add(post)
        session.commit()
        return post, created


class Portal(Base):
    __tablename__ = "portal"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    url = Column(URLType, unique=True, nullable=False)
    slug = Column(URLType, unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    entries: Mapped[List["Entry"]] = relationship(back_populates="portal")

    def __repr__(self):
        return f"{self.name} ({self.url})"


class Entry(Base):
    __tablename__ = "entry"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    portal_id: Mapped[int] = mapped_column(ForeignKey("portal.id"))
    title = Column(String, nullable=False)
    url = Column(URLType, nullable=False)
    screenshot = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    portal: Mapped["Portal"] = relationship(back_populates="entries")
    ads: Mapped[List["Advertisement"]] = relationship(back_populates="entry")

    def save_screenshot(self, session, file_path):
        if file_path is None:
            return
        with suppress(Exception):
            url = upload_file(
                file_path,
                f"screenshots/entries/{folder_date()}/{now()}_{slugify(self.url)[:100]}.png"
            )
            self.screenshot = url
            session.commit()

    def __repr__(self):
        return f"{self.portal.name}: {self.url} - ({self.created_at})"


class Advertisement(Base):
    __tablename__ = "advertisement"

    id = Column(Integer, primary_key=True)
    entry_id: Mapped[int] = mapped_column(ForeignKey("entry.id"))
    url = Column(URLType, nullable=False)
    title = Column(String, nullable=False)
    tag = Column(String, nullable=True)
    thumbnail = Column(URLType, nullable=True)
    screenshot = Column(String, nullable=True)
    excerpt = Column(String, nullable=True)
    media = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    entry: Mapped["Entry"] = relationship(back_populates="ads")

    @classmethod
    def save_screenshot(cls, file_path, url):
        if file_path is None or url is None:
            return
        with suppress(Exception):
            return upload_file(
                file_path,
                f"screenshots/ads/{folder_date()}/{now()}_{slugify(url[:100])}.png"
            )

    @classmethod
    def save_media(cls, url):
        if media_path := dowload_media(url):
            return upload_file(
                media_path,
                f"medias/ads/{folder_date()}/{now()}_{slugify(url[:100])}.png"
            )

    def __repr__(self):
        return f"{self.url}: ({self.entry.url})"


class URLQueue(Base):
    __tablename__ = "urlqueue"

    id = Column(Integer, primary_key=True)
    url = Column(URLType, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    def __repr__(self):
        return f"{self.url}- {self.created_at}"


def get_or_create(session, model, defaults=None, **kwargs):
    instance = session.query(model).filter_by(**kwargs).one_or_none()
    if instance:
        return instance, False
    else:
        kwargs |= defaults or {}
        instance = model(**kwargs)
        try:
            session.add(instance)
            session.commit()
        except Exception:
            session.rollback()
            instance = session.query(model).filter_by(**kwargs).one()
            return instance, False
        else:
            return instance, True


def create_instance(session, model, **kwargs):
    instance = model(**kwargs)
    session.add(instance)
    session.commit()
    return instance

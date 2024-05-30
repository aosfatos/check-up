import sched
import time
import traceback

from decouple import config
from loguru import logger
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from plays.base import BasePlay
from models import Advertisement, Entry, Portal, URLQueue, create_instance

scheduler = sched.scheduler(time.time, time.sleep)

duration = 1


def event_loop():
    main()
    scheduler.enter(duration, 1, event_loop)


def run():
    event_loop()
    scheduler.run()


def main():
    engine = create_engine(config("DATABASE_URL"))
    session = Session(engine)

    url_obj = URLQueue.next(session)
    if url_obj is None:
        logger.info("Queue is empty")
        return

    logger.info(f"Processing URL '{url_obj.url}' from queue...")
    url_obj.set_as_started(session)

    url = url_obj.url
    try:
        scraper = BasePlay.get_scraper(url, headless=config("HEADLESS", cast=bool))
        entry_item = scraper.execute()
    except Exception as exc:
        logger.error(f"Error scraping '{url}': {exc!r}")
        url_obj.set_as_error(session, info=str(traceback.format_exc()))

    if entry_item is None:
        session.close()
        return

    portal = session.query(Portal).filter_by(slug=scraper.name).one()

    logger.info(f"Saving entry '{entry_item.title}'")
    entry = create_instance(
        session,
        Entry,
        portal=portal,
        url=entry_item.url,
        title=entry_item.title,
    )
    entry.save_screenshot(session, entry_item.screenshot_path)
    logger.info(f"Saved entry with id: {entry.id}")
    ads = []
    for ad_item in entry_item.ads:
        logger.info(f"[{entry.id}] Saving AD: '{ad_item.title}'")
        ad_screenshot_url = Advertisement.save_screenshot(
            ad_item.screenshot_path,
            ad_item.url,
        )
        ad_media_url = Advertisement.save_media(ad_item.thumbnail_url)
        ads.append(
            Advertisement(
                entry=entry,
                title=ad_item.title,
                url=ad_item.url,
                thumbnail=ad_item.thumbnail_url,
                screenshot=ad_screenshot_url,
                media=ad_media_url,
                tag=ad_item.tag,
                excerpt=ad_item.excerpt,
            )
        )

    logger.info(f"[{entry.id}] Saving {len(ads)} ads to database")
    session.add_all(ads)
    session.commit()
    logger.info(f"[{portal.slug}] Done scraping entry {entry.id}")

    url_obj.set_as_finished(session)
    session.close()


if __name__ == "__main__":
    run()

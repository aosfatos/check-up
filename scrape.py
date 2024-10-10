import sched
import time
import traceback

from decouple import config
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from plays.base import BasePlay
from plog import logger
from llm.analysis import classify_ad
from llm.internal_url import is_internal
from models import (
    Advertisement,
    Entry,
    Portal,
    URLQueue,
    create_instance,
    get_classification,
)

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

    url_obj = URLQueue.next_random(session)
    if url_obj is None:
        logger.info("Queue is empty")
        session.close()
        return

    logger.info(f"Processing URL '{url_obj.url}' from queue...")
    url_obj.set_as_started(session)

    url = url_obj.url
    entry_item = None
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
    n_ads = len(entry_item.ads)
    for i, ad_item in enumerate(entry_item.ads, start=1):

        if not ad_item.is_valid():
            logger.warning(f"[{portal.slug}] Ad {ad_item} is not valid")
            continue

        if not is_internal(ad_item.url):
            logger.info(
                f"[{portal.slug}] Looking for existing classfication "
                f"({i}/{n_ads}): '{ad_item.title} - {ad_item.tag}'"
            )
            category, category_verbose = get_classification(
                session,
                ad_item.title,
                ad_item.tag,
            )
            if category is None:
                try:
                    category, category_verbose = classify_ad(ad_item.title, ad_item.tag)
                    logger.info(
                        f"[{portal.slug}] Classified AD with LLM "
                        f"({i}/{n_ads}): '{ad_item.title}' - category: '{category}"
                    )
                except Exception as exc:
                    logger.error(
                        f"[{portal.slug}] Error classifying ad ({i}/{n_ads}): {exc}"
                    )
            else:
                logger.info(
                    f"[{portal.slug}] Found AD classification on DB "
                    f"({i}/{n_ads}): '{ad_item.title}' - '{category}'"
                )
        else:
            category = None
            category_verbose = None
            logger.warning(
                f"[{portal.slug}] Ad URL is internal ({i}/{n_ads}): '{ad_item.url}'"
            )

        logger.info(f"[{portal.slug}] Saving AD ({i}/{n_ads}): '{ad_item.title}'")
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
                category=category,
                category_verbose=category_verbose,
            )
        )

    logger.info(f"[{portal.slug}] Saving {len(ads)} ads to database")
    session.add_all(ads)
    session.commit()
    logger.info(f"[{portal.slug}] Done scraping entry {entry.id}")

    url_obj.set_as_finished(session)
    session.close()


if __name__ == "__main__":
    run()

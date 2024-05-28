from decouple import config
from loguru import logger
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from plays.base import BasePlay
from models import Advertisement, Entry, Portal, create_instance


if __name__ == "__main__":
    urls = [u.strip() for u in open("urls.txt", "r")]

    engine = create_engine(config("DATABASE_URL"))
    session = Session(engine)
    for url in urls:
        scraper = BasePlay.get_scraper(url, headless=config("HEADLESS", cast=bool))
        entry_item = scraper.execute()
        if entry_item is None:
            continue

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
                )
            )

        logger.info(f"[{entry.id}] Saving {len(ads)} ads to database")
        session.add_all(ads)
        session.commit()
        logger.info("Done!")

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
        scrapper = BasePlay.get_scrapper(url, headless=True)
        result = scrapper.execute()
        if result is None:
            continue

        # TODO: improve this query
        portal = session.query(Portal).filter_by(name=scrapper.name.capitalize()).one()

        logger.info(f"Saving entry {result['entry_title']} on database")
        entry = create_instance(
            session,
            Entry,
            portal=portal,
            url=result["entry_url"],
            title=result["entry_title"],
        )
        entry.save_screenshot(result["entry_screenshot_path"])
        ads = []
        for ad_item in result["ad_items"]:
            logger.info(f"Uploading AD {ad_item['ad_title']} screenshot")
            # ad_screenshot_url = upload_file(
            #     ad_item["screenshot_path"],
            #     f"{now()}_{slugify(ad_item['ad_url'])}",
            #     type_="ads",
            # )
            ads.append(
                Advertisement(
                    entry=entry,
                    title=ad_item["ad_title"],
                    url=ad_item["ad_url"],
                    thumbnail=ad_item["thumbnail_url"],
                    tag=ad_item["tag"],
                )
            )

        logger.info(f"Saving {len(ads)} ads to database")
        session.add_all(ads)
        session.commit()
        logger.info("Done!")

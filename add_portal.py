import argparse

from decouple import config
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from slugify import slugify

from models import Portal
from plog import logger


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="Add new portal")
    parser.add_argument("portal_name", help="Name of the Portal")
    parser.add_argument("portal_url", help="URL of the Portal")
    args = parser.parse_args()

    engine = create_engine(config("DATABASE_URL"))
    slug = slugify(args.portal_name)
    logger.info(
        f"Adding new portal: {args.portal_name}({slug}): (args.portal_url)"
    )
    portal = Portal(name=args.portal_name, url=args.portal_url, slug=slug)

    with Session(engine) as session:
        session.add(portal)
        session.commit()

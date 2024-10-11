from decouple import config
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from models import (
    Advertisement,
    Portal,
    Entry,
    QueueStatus,
    URLQueue,
)


if __name__ == "__main__":
    engine = create_engine(config("DATABASE_URL"))

    Portal.metadata.create_all(engine)
    Entry.metadata.create_all(engine)
    Advertisement.metadata.create_all(engine)
    URLQueue.metadata.create_all(engine)
    QueueStatus.metadata.create_all(engine)

    portals = [
        ("UOL", "https://noticias.uol.com.br/", "uol"),
        ("Folha", "https://www.folha.uol.com.br/", "folha"),
        ("Estadão", "https://www.estadao.com.br/", "estadao"),
        ("Veja", "https://veja.abril.com.br/", "veja"),
        ("Terra", "https://www.terra.com.br/", "terra"),
        ("Metropoles", "https://www.metropoles.com/", "metropoles"),
        ("ClicRBS", "https://clicrbs.com.br/", "clicrbs"),
        ("Globo", "https://oglobo.globo.com/", "globo"),
        ("IG", "https://www.ig.com.br/", "ig"),
        ("R7", "https://www.r7.com/", "r7"),
    ]
    portals_to_add = []
    for portal in portals:
        portals_to_add.append(Portal(name=portal[0], url=portal[1], slug=portal[2]))

    with Session(engine) as session:
        session.add_all(portals_to_add)
        session.commit()

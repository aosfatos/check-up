from datetime import datetime

from decouple import config
from loguru import logger
from slugify import slugify
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from plays.base import BasePlay
from models import Advertisement, Entry, Portal, get_or_create
from storage import upload_file


def now():
    return datetime.now().strftime("%Y%m%d%H%M%S")


if __name__ == "__main__":
    urls = [
        # folha
        "https://www1.folha.uol.com.br/mercado/2024/05/com-magda-chambriard-petrobras-tera-sexto-presidente-em-tres-anos.shtml",
        "https://www1.folha.uol.com.br/tec/2024/05/google-usara-ia-para-detectar-tentativas-de-golpes-em-ligacoes-em-celulares-android.shtml",
        "https://www1.folha.uol.com.br/cotidiano/2024/05/motorista-de-porsche-aparece-dentro-de-carro-momentos-antes-do-acidente.shtml",
        "https://www1.folha.uol.com.br/mercado/2024/05/como-comprar-a-casa-propria-por-consorcio.shtml",
        "https://www1.folha.uol.com.br/ciencia/2024/05/estudo-revela-evidencias-de-violencia-em-uma-epoca-de-crise-no-antigo-peru.shtml",
        # estadao
        "https://www.estadao.com.br/economia/prates-petrobras-costa-silveira-analise/",
        "https://www.estadao.com.br/ciencia/pesquisadores-da-usp-criam-mapa-interativo-com-sitios-arqueologicos-de-sp-veja-locais-nprm/",
        "https://www.estadao.com.br/politica/condenados-8-janeiro-2023-vandalismo-ataques-tres-poderes-quebram-tornozeleira-eletronica-fogem-do-pais-argentina-uruguai-vejam-quem-sao-nprp/",
        "https://www.estadao.com.br/esportes/futebol/ronaldo-empresario-venda-saf-cruzeiro/",
        "https://www.estadao.com.br/saude/sinais-precoces-de-alzheimer-podem-comecar-pelos-olhos-sugere-estudo-veja-o-que-isso-significa/",
        # veja
        "https://veja.abril.com.br/economia/petrobras-desaba-quase-10-em-ny-apos-demissao-de-prates/",
        "https://veja.abril.com.br/mundo/putin-volta-a-visitar-xi-jinping-em-teste-de-parceria-sem-limites/",
        "https://veja.abril.com.br/mundo/de-guitarra-na-mao-blinken-reforca-apoio-inabalavel-dos-eua-a-ucrania/",
        "https://veja.abril.com.br/coluna/tela-plana/beleza-fatal-os-indicios-capciosos-em-trailer-da-primeira-novela-da-hbo/",
        "https://veja.abril.com.br/politica/justica-arquiva-inquerito-que-investigou-ex-ministro-por-crime-ambiental/",
        # uol
        "https://www1.folha.uol.com.br/cotidiano/2024/05/com-milhares-de-pessoas-fora-de-casa-e-guaiba-em-alta-rs-planeja-manter-abrigos-por-meses.shtml",
        "https://noticias.uol.com.br/colunas/andre-santana/2024/05/15/ha-135-anos-bembe-do-mercado-celebra-religiao-que-anitta-exalta-em-aceita.htm",
        "https://www.uol.com.br/esporte/futebol/colunas/rafael-reis/2024/05/15/libertadores-entenda-por-que-o-del-valle-torce-por-titulo-do-palmeiras.htm",

        "https://noticias.uol.com.br/colunas/jamil-chade/2024/05/15/lider-de-partido-alemao-aliado-a-bolsonaro-e-condenado-por-slogan-nazista.htm",
        "https://www.uol.com.br/splash/colunas/lucas-pasin/2024/05/15/filme-com-isis-valverde-e-grazi-massafera-tem-burburinho-nos-bastidores.htm",

    ]

    urls = [
        # folha
        "https://www1.folha.uol.com.br/ciencia/2024/05/estudo-revela-evidencias-de-violencia-em-uma-epoca-de-crise-no-antigo-peru.shtml",
        # estadao
        "https://www.estadao.com.br/saude/sinais-precoces-de-alzheimer-podem-comecar-pelos-olhos-sugere-estudo-veja-o-que-isso-significa/",
        # veja
        "https://veja.abril.com.br/politica/justica-arquiva-inquerito-que-investigou-ex-ministro-por-crime-ambiental/",
        # uol
        "https://noticias.uol.com.br/colunas/jamil-chade/2024/05/15/lider-de-partido-alemao-aliado-a-bolsonaro-e-condenado-por-slogan-nazista.htm",

    ]

    engine = create_engine(config("DATABASE_URL"))
    session = Session(engine)
    for url in urls:
        scrapper = BasePlay.get_scrapper(url, headless=True)
        result = scrapper.execute()
        if result is None:
            continue
        # TODO: improve this query
        portal = session.query(Portal).filter_by(name=scrapper.name.capitalize()).one()
        logger.info(f"Uploading entry {result['entry_title']} screenshot")
        entry_screenshot_url = upload_file(
            result["entry_screenshot_path"],
            f"{now()}_{slugify(result['entry_url'])}",
            type_="entry",
        )
        logger.info(f"Saving entry {result['entry_title']} on database")
        entry, _ = get_or_create(
            session,
            Entry,
            portal=portal,
            screenshot=entry_screenshot_url,
            url=result["entry_url"], defaults={"title": result["entry_title"]}
        )
        ads = []
        for ad_item in result["ad_items"]:
            logger.info(f"Uploading AD {ad_item['ad_title']} screenshot")
            ad_screenshot_url = upload_file(
                ad_item["screenshot_path"],
                f"{now()}_{slugify(ad_item['ad_url'])}",
                type_="ads",
            )
            ads.append(
                Advertisement(
                    entry=entry,
                    title=ad_item["ad_title"],
                    url=ad_item["ad_url"],
                    thumbnail=ad_item["thumbnail_url"],
                    screenshot=ad_screenshot_url,
                    tag=ad_item["tag"],
                )
            )

        logger.info(f"Saving {len(ads)} ads to database")
        session.add_all(ads)
        session.commit()
        logger.info("Done!")

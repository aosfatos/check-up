from plays.base import BasePlay


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

    for url in urls:
        scrapper = BasePlay.get_scrapper(url, headless=True)
        result = scrapper.execute()
        print("RESULT", result)

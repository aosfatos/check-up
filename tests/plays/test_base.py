import pytest
from freezegun import freeze_time

from plays.base import BasePlay
from plays import (
    ClicRBSPlay,
    EstadaoPlay,
    FolhaPlay,
    GloboPlay,
    IGPlay,
    MetropolesPlay,
    VejaPlay,
    TerraPlay,
    UOLPlay
)
from plays.exceptions import ScraperNotFoundError


class TestBasePlay:
    def test_return_correct_scraper_folha(self):
        url = "https://www1.folha.uol.com.br/mundo/2024/05/entry-slug"

        scraper = BasePlay.get_scraper(url)

        assert isinstance(scraper, FolhaPlay)
        assert scraper.url == url

    def test_return_correct_scraper_estadao(self):
        url = "https://www.estadao.com.br/economia/entry-slug"

        scraper = BasePlay.get_scraper(url)

        assert isinstance(scraper, EstadaoPlay)
        assert scraper.url == url

    def test_return_correct_scraper_veja(self):
        url = "https://veja.abril.com.br/economia/entry-slug"

        scraper = BasePlay.get_scraper(url)

        assert isinstance(scraper, VejaPlay)
        assert scraper.url == url

    def test_return_correct_scraper_uol(self):
        url = "https://noticias.uol.com.br/cotidiano/ultimas-noticias/entry-slug"

        scraper = BasePlay.get_scraper(url)

        assert isinstance(scraper, UOLPlay)
        assert scraper.url == url

    def test_return_correct_scraper_globo(self):
        url = "https://oglobo.globo.com/economia/noticia/entry-slug"

        scraper = BasePlay.get_scraper(url)

        assert isinstance(scraper, GloboPlay)
        assert scraper.url == url

    def test_return_correct_scraper_terra(self):
        url = "https://www.terra.com.br/esportes/futebol/internacional/entry-slug"

        scraper = BasePlay.get_scraper(url)

        assert isinstance(scraper, TerraPlay)
        assert scraper.url == url

    def test_return_correct_scraper_metropoles(self):
        url = "https://www.metropoles.com/brasil/entry-slug"

        scraper = BasePlay.get_scraper(url)

        assert isinstance(scraper, MetropolesPlay)
        assert scraper.url == url

    def test_return_correct_scraper_clic_rbs(self):
        url = "https://gauchazh.clicrbs.com.br/ambiente/noticia/entry-slug"

        scraper = BasePlay.get_scraper(url)

        assert isinstance(scraper, ClicRBSPlay)
        assert scraper.url == url

    def test_return_correct_scraper_ig(self):
        url = "https://ultimosegundo.ig.com.br/brasil/entry-slug"

        scraper = BasePlay.get_scraper(url)

        assert isinstance(scraper, IGPlay)
        assert scraper.url == url

    def test_raise_error_if_no_scraper_is_found(self):
        url = "https://any.com.br"

        with pytest.raises(ScraperNotFoundError):
            BasePlay.get_scraper(url)

    @freeze_time("2024-05-15 12:00:00")
    def test_get_session(self):
        url = "https://entry-url.com"

        scraper = BasePlay(url, session_dir="/tmp/session")

        assert scraper.get_session_dir() == "/tmp/session"

    @freeze_time("2024-05-15 12:00:00")
    def test_get_session_when_not_given(self):
        url = "https://entry-url.com"

        scraper = BasePlay(url)

        assert scraper.get_session_dir() == "/tmp/base_session/"

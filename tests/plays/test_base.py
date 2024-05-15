import pytest
from freezegun import freeze_time

from plays.base import BasePlay
from plays.exceptions import ScrapperNotFoundError
from plays.estadao import EstadaoPlay
from plays.folha import FolhaPlay
from plays.veja import VejaPlay
from plays.uol import UOLPlay


class TestBasePlay:
    def test_return_correct_scrapper_folha(self):
        url = "https://www1.folha.uol.com.br/mundo/2024/05/entry-slug"

        scrapper = BasePlay.get_scrapper(url)

        assert isinstance(scrapper, FolhaPlay)
        assert scrapper.url == url

    def test_return_correct_scrapper_estadao(self):
        url = "https://www.estadao.com.br/economia/entry-slug"

        scrapper = BasePlay.get_scrapper(url)

        assert isinstance(scrapper, EstadaoPlay)
        assert scrapper.url == url

    def test_return_correct_scrapper_veja(self):
        url = "https://veja.abril.com.br/economia/entry-slug"

        scrapper = BasePlay.get_scrapper(url)

        assert isinstance(scrapper, VejaPlay)
        assert scrapper.url == url

    def test_return_correct_scrapper_uol(self):
        url = "https://noticias.uol.com.br/cotidiano/ultimas-noticias/entry-slug"

        scrapper = BasePlay.get_scrapper(url)

        assert isinstance(scrapper, UOLPlay)
        assert scrapper.url == url

    def test_raise_error_if_no_scrapper_is_found(self):
        url = "https://any.com.br"

        with pytest.raises(ScrapperNotFoundError):
            BasePlay.get_scrapper(url)

    @freeze_time("2024-05-15 12:00:00")
    def test_get_session(self):
        url = "https://entry-url.com"

        scrapper = BasePlay(url, session_dir="/tmp/session")

        assert scrapper.get_session_dir() == "/tmp/session"

    @freeze_time("2024-05-15 12:00:00")
    def test_get_session_when_not_given(self):
        url = "https://entry-url.com"

        scrapper = BasePlay(url)

        assert scrapper.get_session_dir() == "/tmp/base_session"

from plays.uol import UOLPlay


class TestUOLPlay:
    def test_match(self):
        assert UOLPlay.match("https://noticias.uol.com.br/colunas/") is True
        assert UOLPlay.match("https://www.uol.com.br/colunas/") is True

from urllib.parse import urlparse


mapper = {
    "clicrbs": ["gauchazh.clicrbs.com.br"],
    "estadao": ["www.estadao.com.br"],
    "folha": ["folha.uol.com.br"],
    "ig": ["ig.com.br"],
    "globo": ["globo.com", "techtudo.com.br"],
    "r7": ["r7.com"],
    "metropoles": ["metropoles.com"],
    "uol": ["uol.com.br"],
}


def is_internal(url):
    try:
        url = urlparse(url).netloc
    except Exception:
        pass
    portal_urls = [
        "gauchazh.clicrbs.com.br",
        "www.estadao.com.br",
        "estadao.com.br",
        "folha.uol.com.br",
        "ig.com.br",
        "globo.com",
        "techtudo.com.br",
        "r7.com",
        "metropoles.com",
        "uol.com.br"
    ]
    for portal_url in portal_urls:
        if portal_url in url:
            return True

    return False

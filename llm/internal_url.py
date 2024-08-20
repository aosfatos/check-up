import pandas
from tqdm import tqdm

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
    portal_urls = [
        "gauchazh.clicrbs.com.br",
        "www.estadao.com.br",
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


if __name__ == "__main__":
    df = pandas.read_excel("stratified_sampling_31_07_2024_llm.xlsx")
    df["internal_link"] = None

    for index, row in enumerate(df.itertuples()):
        df.loc[index, "internal_link"] = is_internal(row.url)

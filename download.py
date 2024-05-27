from tempfile import NamedTemporaryFile


import requests
from tenacity import retry, stop_after_attempt, wait_fixed


@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
def dowload_media(url):
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    temp_file = NamedTemporaryFile(suffix=".png", delete=False)
    with open(temp_file.name, "wb") as fobj:
        fobj.write(resp.content)
    return temp_file.name

from tempfile import NamedTemporaryFile


import requests
from tenacity import retry, stop_after_attempt, wait_fixed

from plog import logger


@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
def _download_media(url):
    if url is None:
        return
    logger.info(f"Downloading media {url}...")
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    temp_file = NamedTemporaryFile(suffix=".png", delete=False)
    with open(temp_file.name, "wb") as fobj:
        fobj.write(resp.content)
    logger.info("Done")
    return temp_file.name


def download_media(url):
    media = None
    try:
        media = _download_media(url)
    except Exception:
        logger.info(f"Error downloadinf media {url}")

    return media

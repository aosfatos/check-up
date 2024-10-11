from llm.analysis import classify_ad
from llm.internal_url import is_internal
from models import get_classification
from plog import logger


def get_or_classify_ad(session, ad_item, portal, i, n_ads):
    if not is_internal(ad_item.url):
        logger.info(
            f"[{portal.slug}] Looking for existing classfication "
            f"({i}/{n_ads}): '{ad_item.title} - {ad_item.tag}'"
        )
        category, category_verbose = get_classification(
            session,
            ad_item.title,
            ad_item.tag,
        )
        if category is None:
            try:
                category, category_verbose = classify_ad(ad_item.title, ad_item.tag)
                logger.info(
                    f"[{portal.slug}] Classified AD with LLM "
                    f"({i}/{n_ads}): '{ad_item.title}' - category: '{category}"
                )
            except Exception as exc:
                logger.error(
                    f"[{portal.slug}] Error classifying ad ({i}/{n_ads}): {exc}"
                )
        else:
            logger.info(
                f"[{portal.slug}] Found AD classification on DB "
                f"({i}/{n_ads}): '{ad_item.title}' - '{category}'"
            )
    else:
        category = None
        category_verbose = None
        logger.warning(
            f"[{portal.slug}] Ad URL is internal ({i}/{n_ads}): '{ad_item.url}'"
        )

    return category, category_verbose

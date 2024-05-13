import re


def get_or_none(pattern, html_content):
    result = None
    if match_ := re.search(pattern, html_content):
        result = match_.group(1)

    return result

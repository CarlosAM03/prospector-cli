import re


def is_phone(text):

    return bool(
        re.search(
            r"\d{3}[\s-]?\d{3}[\s-]?\d{4}",
            text
        )
    )
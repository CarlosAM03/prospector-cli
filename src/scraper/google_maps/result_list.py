from models.business import Business

from .parser import parse_business_summary
from .selectors import (
    RESULT_LINK,
    RESULT_ARTICLE,
    INFO_BLOCK,
)


def extract_businesses(page, limit):

    businesses = []

    links = page.locator(
        RESULT_LINK
    )

    print(
        "Lugares encontrados:",
        links.count()
    )

    total = min(
        links.count(),
        limit
    )

    for index in range(total):

        link = links.nth(index)

        if index == 0:

            print(
                link.evaluate(
                    "(element)=>element.parentElement.outerHTML"
                )
            )

        name = link.get_attribute(
            "aria-label"
        )

        article = link.locator(
            RESULT_ARTICLE
        )

        info_blocks = article.locator(
            INFO_BLOCK
        )

        category, address, phone = parse_business_summary(
            info_blocks
        )

        if name:

            businesses.append(
                Business(
                    name=name,
                    category=category,
                    address=address,
                    phone=phone
                )
            )

    print(
        "Negocios extraídos:",
        len(businesses)
    )

    return businesses
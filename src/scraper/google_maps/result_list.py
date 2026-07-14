from models.business import Business

from .parser import parse_business_summary
from .selectors import create_selector_engine


def extract_businesses(
    page,
    limit: int,
):

    businesses = []

    selector = create_selector_engine(
        page
    )

    links = selector.locator(
        "results"
    )

    print(
        "Lugares encontrados:",
        links.count()
    )

    total = min(
        links.count(),
        limit,
    )

    for index in range(total):

        link = links.nth(index)

        name = link.get_attribute(
            "aria-label"
        )

        href = link.get_attribute(
            "href"
        )

        if not name or not href:
            continue

        article = link.locator(
            selector.selectors(
                "result_article"
            )[0]
        )

        info_blocks = article.locator(
            selector.selectors(
                "info_block"
            )[0]
        )

        category, address, phone = parse_business_summary(
            info_blocks
        )

        businesses.append(
            {
                "href": href,
                "business": Business(
                    name=name,
                    category=category,
                    address=address,
                    phone=phone,
                ),
            }
        )

    print(
        "Negocios encontrados:",
        len(businesses)
    )

    return businesses
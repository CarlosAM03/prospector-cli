from models.business import Business

from .parser import parse_business_summary
from .selectors import create_selector_engine


def extract_businesses(
    page,
    limit: int,
):
    """
    Extract businesses from Google Maps result list.

    This stage only extracts summary information.

    Detailed enrichment is performed later by the
    detail panel pipeline.

    Parameters
    ----------
    page:
        Playwright page instance.

    limit:
        Maximum number of businesses to extract.

    Returns
    -------
    list[dict]

    Each item contains:

    {
        "href": Google Maps place URL,
        "business": Business instance
    }

    Notes
    -----
    This function does not:

    - Open detail panels.
    - Extract website information.
    - Perform website inspection.
    """

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

        link = links.nth(
            index
        )


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


        category, address, phone = (
            parse_business_summary(
                info_blocks
            )
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
from models.business import Business

from engines.selector.lazycharge import LazyChargeEngine

from .parser import parse_business_summary
from .selectors import create_selector_engine


PROFILE = "google_maps"


def extract_businesses(
    page,
    limit: int,
):
    """
    Extract businesses from Google Maps result list.

    This stage only extracts summary information.

    Before extraction, the scraper waits until the
    results feed is available and progressively loads
    additional results through virtual scrolling.

    Parameters
    ----------
    page:
        Playwright page instance.

    limit:
        Maximum number of businesses to extract.
    """

    businesses = []

    selector = create_selector_engine(
        page
    )

    lazycharge = LazyChargeEngine(
        page=page,
        profile=PROFILE,
    )

    #
    # Wait until the Google Maps
    # result feed is visible.
    #

    lazycharge.wait(
        "feed"
    )

    links = selector.locator(
        "results"
    )

    #
    # Load additional results before
    # performing the first extraction.
    #

    _charge_results(
        page=page,
        selector=selector,
        limit=limit,
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


def _charge_results(
    page,
    selector,
    limit: int,
):
    """
    Scroll the Google Maps result panel until
    enough results are loaded or loading stops.
    """

    feed = selector.locator(
        "feed"
    )

    links = selector.locator(
        "results"
    )

    previous_count = -1

    stable_cycles = 0

    max_stable_cycles = 4


    while True:

        current_count = links.count()

        print(
            "Antes:",
            current_count,
        )


        if current_count >= limit:

            print(
                "Límite alcanzado."
            )

            break


        if current_count == previous_count:

            stable_cycles += 1

        else:

            stable_cycles = 0


        if stable_cycles >= max_stable_cycles:

            print(
                "Google Maps dejó de cargar resultados."
            )

            break


        previous_count = current_count


        #
        # Scroll únicamente el panel
        # izquierdo de resultados.
        #

        feed.hover()

        page.mouse.wheel(
            0,
            1800,
        )


        page.wait_for_timeout(
            1000,
        )


        print(
            "Después:",
            links.count(),
        )


    print(
        "Resultados cargados:",
        links.count(),
    )
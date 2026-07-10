from playwright.sync_api import sync_playwright

from .detail_panel import enrich_business
from .result_list import extract_businesses
from .search import create_search_page
from .selectors import RESULT_LINK


def search_businesses(
    query,
    limit=50
):

    with sync_playwright() as playwright:

        browser = playwright.chromium.launch(
            headless=False
        )

        page = create_search_page(
            browser,
            query
        )

        #
        # Fase 1
        #

        results = extract_businesses(
            page,
            limit
        )

        businesses = []

        #
        # Fase 2
        #

        for result in results:

            link = page.locator(
                RESULT_LINK
            ).nth(
                result["index"]
            )

            business = enrich_business(
                page,
                link,
                result["business"]
            )

            businesses.append(
                business
            )

        browser.close()

        return businesses
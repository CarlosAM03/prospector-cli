import time

from playwright.sync_api import sync_playwright

from models.business import Business
from models.search_query import SearchQuery
from models.search_result import SearchResult

from .detail_panel import enrich_business
from .result_list import extract_businesses
from .search import create_search_page
from .website_enrichment import enrich_websites


def search_businesses(
    query: SearchQuery,
    limit: int = 50,
) -> SearchResult:
    """
    Execute the complete Google Maps scraping pipeline.

    Pipeline
    --------

    Phase 1
        Extract search results.

    Phase 2
        Enrich businesses using the Google Maps detail panel.

    Phase 3
        Inspect business websites.

    Returns
    -------
    SearchResult
    """

    start_time = time.perf_counter()

    with sync_playwright() as playwright:

        browser = playwright.chromium.launch(
            headless=False,
        )

        page = create_search_page(
            browser,
            query,
        )

        #
        # Phase 1
        # Extract search results.
        #

        results = extract_businesses(
            page=page,
            limit=limit,
        )

        #
        # Phase 2
        # Enrich businesses using
        # the Google Maps detail panel.
        #

        businesses = _enrich_businesses(
            page=page,
            results=results,
        )

        #
        # Phase 3
        # Inspect business websites.
        #

        businesses = enrich_websites(
            browser=browser,
            businesses=businesses,
        )

        browser.close()

    execution_time = (
        time.perf_counter()
        - start_time
    )

    return SearchResult(
        query=query,
        businesses=businesses,
        execution_time=execution_time,
    )


def _enrich_businesses(
    page,
    results: list[dict],
) -> list[Business]:
    """
    Execute Google Maps detail panel enrichment.
    """

    businesses: list[Business] = []

    for result in results:

        business = enrich_business(
            page=page,
            href=result["href"],
            business=result["business"],
        )

        businesses.append(
            business
        )

    return businesses
import time

from playwright.sync_api import sync_playwright

from models.search_query import (
    SearchQuery,
    Source,
)
from models.search_result import SearchResult

from .detail_panel import enrich_business
from .result_list import extract_businesses
from .search import create_search_page


def search_businesses(
    query: SearchQuery,
    limit: int = 50
) -> SearchResult:

    start_time = time.perf_counter()

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

            business = enrich_business(
                page,
                result["href"],
                result["business"]
            )

            businesses.append(
                business
            )

        browser.close()

    execution_time = (
        time.perf_counter() - start_time
    )

    return SearchResult(
        query=query,
        businesses=businesses,
        execution_time=execution_time,
    )
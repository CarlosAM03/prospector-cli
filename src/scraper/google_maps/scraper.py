"""Current three-pass Google Maps extraction entrypoint."""

import time

from engines.browser_runtime import BrowserRuntime

from models.business import Business
from models.search_query import SearchQuery
from models.search_result import SearchResult

from .detail_panel import enrich_business
from .result_list import extract_businesses
from .search import create_search_page
from .website_enrichment import enrich_websites


def search_businesses(query: SearchQuery, limit: int = 50) -> SearchResult:
    """Transitional boundary with its historical defaults and inputs."""
    return _run_google_maps(query, limit, headless=False, website_enrichment=True)


def _run_google_maps(
    query: SearchQuery,
    limit: int,
    *,
    headless: bool,
    website_enrichment: bool,
    issue_collector=None,
) -> SearchResult:
    """Single source pipeline supplied with execution settings."""
    start_time = time.perf_counter()
    with BrowserRuntime(headless=headless) as runtime:
        page = create_search_page(
            runtime.browser, query, page_factory=runtime.new_page
        )
        results = extract_businesses(page=page, limit=limit)
        businesses = _enrich_businesses(
            page=page, results=results, issue_collector=issue_collector
        )
        if website_enrichment:
            businesses = enrich_websites(
                browser=runtime.browser, businesses=businesses,
                issue_collector=issue_collector,
            )
        # Runtime owns the Maps page and browser. WebsiteCrawler closes each
        # short-lived inspection page that it creates.
    return SearchResult(
        query=query,
        businesses=businesses,
        execution_time=time.perf_counter() - start_time,
    )


def _enrich_businesses(page, results: list[dict], issue_collector=None) -> list[Business]:
    businesses: list[Business] = []
    for result in results:
        businesses.append(
            enrich_business(
                page=page,
                href=result["href"],
                business=result["business"],
                identity=result["identity"],
                issue_collector=issue_collector,
            )
        )
    return businesses

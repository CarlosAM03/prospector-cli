"""Current three-pass Google Maps extraction entrypoint."""

import time
from dataclasses import dataclass, field

from engines.browser_runtime import BrowserRuntime
from engines.errors import (
    ProspectorExtractionError,
    ProspectorNavigationError,
    ProspectorRuntimeError,
)
from engines.issue_collector import IssueCollector
from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from models.business import Business
from models.search_query import SearchQuery
from models.search_issue import SearchIssue
from models.search_result import SearchResult
from models.source_identity import SourceIdentityEvidence

from .detail_panel import enrich_business
from .parser import category_repeats_address
from .result_list import extract_businesses
from .search import create_search_page
from .source_identity import verified_place_identity
from .website_enrichment import enrich_websites


@dataclass
class _SourceResult:
    """Consolidated Google Maps output before the global result is assembled."""

    query: SearchQuery
    businesses: list[Business] = field(default_factory=list)
    execution_time: float = 0.0
    issues: list[SearchIssue] = field(default_factory=list)
    identities: list[SourceIdentityEvidence] = field(default_factory=list)

    def __post_init__(self) -> None:
        if len(self.identities) != len(self.businesses):
            raise ValueError("source identity sidecar must match Business count")
        if any(type(item) is not SourceIdentityEvidence for item in self.identities):
            raise TypeError("source identity sidecar contains an invalid item")

    @property
    def total_found(self) -> int:
        return len(self.businesses)


def search_businesses(query: SearchQuery, limit: int = 50) -> SearchResult:
    """Legacy inputs with the mandatory shared global normalization stage."""
    from engines.global_pipeline import execute_global_search

    return execute_global_search(
        _run_google_maps, query, limit,
        headless=False, website_enrichment=True,
    )


def _run_google_maps(
    query: SearchQuery,
    limit: int,
    *,
    headless: bool,
    website_enrichment: bool,
    issue_collector=None,
    typed_errors: bool = False,
    metrics_sink: dict | None = None,
) -> _SourceResult:
    """Single source pipeline supplied with execution settings."""
    start_time = time.perf_counter()
    collector = issue_collector if issue_collector is not None else IssueCollector()
    try:
        with BrowserRuntime(headless=headless) as runtime:
            if metrics_sink is not None:
                metrics_sink["browser_version"] = getattr(
                    runtime.browser, "version", None
                )
            stage_start = time.perf_counter()
            try:
                page = create_search_page(
                    runtime.browser, query, page_factory=runtime.new_page
                )
            except (PlaywrightError, LookupError) as error:
                if typed_errors:
                    raise ProspectorNavigationError(
                        "Google Maps navigation did not reach a usable result view."
                    ) from error
                raise
            if metrics_sink is not None:
                metrics_sink["navigation_seconds"] = time.perf_counter() - stage_start
            stage_start = time.perf_counter()
            try:
                results = extract_businesses(
                    page=page, limit=limit, issue_collector=collector
                )
            except (PlaywrightError, LookupError) as error:
                if typed_errors:
                    raise ProspectorExtractionError(
                        "Google Maps did not produce a verifiable result feed."
                    ) from error
                raise
            if metrics_sink is not None:
                metrics_sink["feed_seconds"] = time.perf_counter() - stage_start
                metrics_sink["observed_candidates"] = len(results)
                summary_fields = [
                    (item["business"].address, item["business"].phone,
                     item["business"].website)
                    for item in results
                ]
            stage_start = time.perf_counter()
            identities: list[SourceIdentityEvidence] = []
            businesses = _enrich_businesses(
                page=page, results=results, issue_collector=collector,
                identity_sink=identities,
            )
            if metrics_sink is not None:
                metrics_sink["detail_seconds"] = time.perf_counter() - stage_start
                metrics_sink["detail_unchanged_count"] = sum(
                    (business.address, business.phone, business.website) == before
                    for business, before in zip(businesses, summary_fields)
                )
            if website_enrichment:
                before_website = tuple(id(business) for business in businesses)
                stage_start = time.perf_counter()
                businesses = enrich_websites(
                    browser=runtime.browser, businesses=businesses,
                    issue_collector=collector,
                )
                if tuple(id(business) for business in businesses) != before_website:
                    raise ValueError("website enrichment changed source identity order")
                if metrics_sink is not None:
                    metrics_sink["website_seconds"] = time.perf_counter() - stage_start
            # Runtime owns the Maps page and browser. WebsiteCrawler closes
            # each short-lived inspection page that it creates.
        if metrics_sink is not None:
            metrics_sink["cleanup_completed"] = True
    except (PlaywrightError, OSError) as error:
        if typed_errors:
            raise ProspectorRuntimeError(
                "The browser runtime could not complete the search."
            ) from error
        raise
    return _SourceResult(
        query=query,
        businesses=businesses,
        execution_time=time.perf_counter() - start_time,
        issues=list(collector.items),
        identities=identities,
    )


def _enrich_businesses(
    page, results: list[dict], issue_collector=None,
    identity_sink: list[SourceIdentityEvidence] | None = None,
) -> list[Business]:
    businesses: list[Business] = []
    for result in results:
        capture: dict = {}
        business = enrich_business(
            page=page,
            href=result["href"],
            business=result["business"],
            identity=result["identity"],
            issue_collector=issue_collector,
            identity_sink=capture,
        )
        if category_repeats_address(business.category, business.address):
            business.category = None
        businesses.append(business)
        if identity_sink is not None:
            identity_sink.append(verified_place_identity(
                result["href"], capture.get("verified_selected_url"),
            ))
    return businesses

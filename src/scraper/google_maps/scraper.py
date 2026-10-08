"""Current three-pass Google Maps extraction entrypoint."""

import time
from dataclasses import dataclass, field

from engines.browser_runtime import BrowserRuntime
from engines._observability import ExecutionEvent, emit
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
    def record_metric(name: str, value) -> None:
        if metrics_sink is not None:
            metrics_sink[name] = value
        emit(ExecutionEvent("metric_updated", name=name, value=value))

    start_time = time.perf_counter()
    collector = issue_collector if issue_collector is not None else IssueCollector()
    try:
        with BrowserRuntime(headless=headless) as runtime:
            record_metric("browser_version", getattr(runtime.browser, "version", None))
            emit(ExecutionEvent("stage_started", "navigation"))
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
            record_metric("navigation_seconds", time.perf_counter() - stage_start)
            emit(ExecutionEvent("stage_completed", "navigation"))
            emit(ExecutionEvent("stage_started", "feed"))
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
            record_metric("feed_seconds", time.perf_counter() - stage_start)
            record_metric("observed_candidates", len(results))
            emit(ExecutionEvent("stage_completed", "feed"))
            if metrics_sink is not None:
                summary_fields = [
                    (item["business"].address, item["business"].phone,
                     item["business"].website)
                    for item in results
                ]
            emit(ExecutionEvent("stage_started", "detail"))
            stage_start = time.perf_counter()
            identities: list[SourceIdentityEvidence] = []
            businesses = _enrich_businesses(
                page=page, results=results, issue_collector=collector,
                identity_sink=identities,
            )
            record_metric("detail_seconds", time.perf_counter() - stage_start)
            emit(ExecutionEvent("stage_completed", "detail"))
            if metrics_sink is not None:
                record_metric("detail_unchanged_count", sum(
                    (business.address, business.phone, business.website) == before
                    for business, before in zip(businesses, summary_fields)
                ))
            if website_enrichment:
                emit(ExecutionEvent("stage_started", "website"))
                before_website = tuple(id(business) for business in businesses)
                stage_start = time.perf_counter()
                businesses = enrich_websites(
                    browser=runtime.browser, businesses=businesses,
                    issue_collector=collector,
                )
                if tuple(id(business) for business in businesses) != before_website:
                    raise ValueError("website enrichment changed source identity order")
                record_metric("website_seconds", time.perf_counter() - stage_start)
                emit(ExecutionEvent("stage_completed", "website"))
            # Runtime owns the Maps page and browser. WebsiteCrawler closes
            # each short-lived inspection page that it creates.
        record_metric("cleanup_completed", True)
    except (PlaywrightError, OSError) as error:
        if typed_errors:
            failure = ProspectorRuntimeError(
                "The browser runtime could not complete the search."
            )
            if getattr(error, "_prospector_cleanup_failed", False):
                failure._prospector_cleanup_failed = True
            raise failure from error
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
    for index, result in enumerate(results, 1):
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
        emit(ExecutionEvent("progress_updated", "detail", current=index, total=len(results)))
    return businesses

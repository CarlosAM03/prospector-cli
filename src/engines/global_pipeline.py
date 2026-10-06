"""Shared global result assembly for supported public search entrypoints."""

import time
from collections.abc import Callable
from typing import Protocol

from engines.issue_collector import IssueCollector
from engines.normalization import NormalizationEngine
from models.business import Business
from models.search_issue import SearchIssue
from models.search_query import SearchQuery
from models.search_result import SearchResult


class _ConsolidatedSourceResult(Protocol):
    query: SearchQuery
    businesses: list[Business]
    issues: list[SearchIssue]


def execute_global_search(
    source_search: Callable[..., _ConsolidatedSourceResult],
    *source_args,
    **source_kwargs,
) -> SearchResult:
    """Run one source, normalize once, and preserve its consolidated originals."""
    started = time.perf_counter()
    source_result = source_search(*source_args, **source_kwargs)
    originals = list(source_result.businesses)
    if any(type(item) is not Business for item in originals):
        raise TypeError("source pipeline must return consolidated Business objects")
    collector = IssueCollector()
    collector.items.extend(source_result.issues)
    normalized = NormalizationEngine().normalize_businesses(
        originals, issue_collector=collector,
    )
    return SearchResult(
        query=source_result.query,
        businesses=normalized,
        original_businesses=originals,
        execution_time=time.perf_counter() - started,
        issues=list(collector.items),
    )

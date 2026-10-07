"""Shared global result assembly for supported public search entrypoints."""

import time
from collections.abc import Callable
from dataclasses import dataclass
from typing import Protocol

from engines.issue_collector import IssueCollector
from engines.normalization import NormalizationEngine
from models.business import Business
from models.search_issue import SearchIssue
from models.search_query import SearchQuery
from models.search_result import SearchResult
from models.source_identity import SourceIdentityEvidence


class _ConsolidatedSourceResult(Protocol):
    query: SearchQuery
    businesses: list[Business]
    issues: list[SearchIssue]
    identities: list[SourceIdentityEvidence]


@dataclass(frozen=True)
class _GlobalExecution:
    result: SearchResult
    identities: tuple[SourceIdentityEvidence, ...]


def execute_global_search(
    source_search: Callable[..., _ConsolidatedSourceResult],
    *source_args,
    **source_kwargs,
) -> SearchResult:
    """Run one source, normalize once, and preserve its consolidated originals."""
    return _execute_global_search(source_search, *source_args, **source_kwargs).result


def execute_global_search_with_identities(
    source_search: Callable[..., _ConsolidatedSourceResult],
    *source_args,
    **source_kwargs,
) -> _GlobalExecution:
    """Private batch path with the aligned source identity sidecar."""
    return _execute_global_search(source_search, *source_args, **source_kwargs)


def _execute_global_search(
    source_search: Callable[..., _ConsolidatedSourceResult],
    *source_args,
    **source_kwargs,
) -> _GlobalExecution:
    started = time.perf_counter()
    source_result = source_search(*source_args, **source_kwargs)
    originals = list(source_result.businesses)
    if any(type(item) is not Business for item in originals):
        raise TypeError("source pipeline must return consolidated Business objects")
    identities = tuple(source_result.identities)
    if len(identities) != len(originals) or any(
        type(item) is not SourceIdentityEvidence for item in identities
    ):
        raise ValueError("source identity sidecar is not aligned")
    collector = IssueCollector()
    collector.items.extend(source_result.issues)
    normalized = NormalizationEngine().normalize_businesses(
        originals, issue_collector=collector,
    )
    result = SearchResult(
        query=source_result.query,
        businesses=normalized,
        original_businesses=originals,
        execution_time=time.perf_counter() - started,
        issues=list(collector.items),
    )
    return _GlobalExecution(result, identities)

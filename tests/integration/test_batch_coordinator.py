"""P93 sequential batch orchestration with offline source substitutes."""

from dataclasses import replace

import pytest

from engines import prospector_engine
from engines.config import EngineConfig
from engines.errors import (
    BatchInterruptedError, ProspectorNavigationError, ProspectorRuntimeError,
)
from engines.normalization import NormalizationEngine
from models.batch import BatchQuery, QueryStatus
from models.business import Business
from models.search_issue import SearchIssue
from models.search_query import SearchQuery, Source
from models.source_identity import SourceIdentityEvidence
from scraper.google_maps.scraper import _SourceResult


def requests(*keywords, limit=2):
    return [
        BatchQuery(SearchQuery(Source.GOOGLE_MAPS, keyword, "Tijuana"), limit)
        for keyword in keywords
    ]


def source_result(query, businesses=None, issues=None):
    businesses = businesses or []
    return _SourceResult(
        query, businesses, issues=issues or [],
        identities=[SourceIdentityEvidence.unverified() for _ in businesses],
    )


def test_three_queries_run_in_order_after_full_snapshot_and_normalize_once(monkeypatch):
    original_requests = requests("A", "B", "C")
    events = []
    active = 0
    normalize_calls = []
    real_normalize = NormalizationEngine.normalize_businesses

    def source(query, limit, **kwargs):
        nonlocal active
        assert active == 0
        active += 1
        events.append((query.keyword, limit, "open"))
        if query.keyword == "A":
            original_requests[1].query.keyword = "CHANGED BY CALLER"
            original_requests[2].query.location = "CHANGED BY CALLER"
        result = source_result(query, [Business(f" {query.keyword} ")])
        active -= 1
        events.append((query.keyword, limit, "close"))
        return result

    def normalize(self, businesses, **kwargs):
        normalize_calls.append(len(businesses))
        return real_normalize(self, businesses, **kwargs)

    monkeypatch.setattr(prospector_engine, "_run_google_maps", source)
    monkeypatch.setattr(NormalizationEngine, "normalize_businesses", normalize)
    engine = prospector_engine.ProspectorEngine(EngineConfig(limit=50))
    batch = engine.search_many(original_requests)
    assert events == [
        ("A", 2, "open"), ("A", 2, "close"),
        ("B", 2, "open"), ("B", 2, "close"),
        ("C", 2, "open"), ("C", 2, "close"),
    ]
    assert normalize_calls == [1, 1, 1]
    assert [entry.status for entry in batch.entries] == [QueryStatus.SUCCESS] * 3
    assert [entry.request.query.keyword for entry in batch.entries] == ["A", "B", "C"]
    assert batch.entries[2].request.query.location == "Tijuana"
    assert [entry.result.businesses[0].name for entry in batch.entries] == ["A", "B", "C"]
    assert all(entry.result.original_businesses[0].name == f" {entry.request.query.keyword} "
               for entry in batch.entries)
    assert batch.total_observations == batch.total_exportable == 3
    assert batch.execution_time >= 0
    assert engine.config.limit == 50


def test_controlled_failure_continues_and_partial_keeps_result(monkeypatch):
    seen = []

    def source(query, limit, **kwargs):
        seen.append(query.keyword)
        if query.keyword == "B":
            raise ProspectorNavigationError("private detail must not leak")
        issues = ([SearchIssue("feed", "partial_results", "Safe.")]
                  if query.keyword == "C" else [])
        return source_result(query, [Business(query.keyword)], issues)

    monkeypatch.setattr(prospector_engine, "_run_google_maps", source)
    batch = prospector_engine.ProspectorEngine(EngineConfig()).search_many(requests("A", "B", "C"))
    assert seen == ["A", "B", "C"]
    assert [entry.status for entry in batch.entries] == [
        QueryStatus.SUCCESS, QueryStatus.FAILED, QueryStatus.PARTIAL,
    ]
    assert batch.entries[1].result is None
    assert batch.entries[1].export_indices == []
    assert "private detail" not in batch.entries[1].error.message
    assert batch.entries[2].result.issues[0].code == "partial_results"
    assert batch.total_observations == 2


def test_recoverable_issue_without_partial_marker_has_distinct_status(monkeypatch):
    monkeypatch.setattr(
        prospector_engine, "_run_google_maps",
        lambda q, limit, **kwargs: source_result(
            q, [Business("Cafe")], [SearchIssue("website", "inspection_unavailable", "Safe.")],
        ),
    )
    batch = prospector_engine.ProspectorEngine(EngineConfig()).search_many(requests("A"))
    assert batch.entries[0].status is QueryStatus.SUCCESS_WITH_ISSUES
    assert batch.entries[0].result.total_found == 1


@pytest.mark.parametrize("failure,reason", [
    (RuntimeError("programming defect"), "critical_failure"),
    (ProspectorRuntimeError("cleanup unknown"), "critical_failure"),
])
def test_unexpected_or_runtime_failure_interrupts_with_completed_prefix(monkeypatch, failure, reason):
    seen = []

    def source(query, limit, **kwargs):
        seen.append(query.keyword)
        if query.keyword == "B":
            raise failure
        return source_result(query, [Business(query.keyword)])

    monkeypatch.setattr(prospector_engine, "_run_google_maps", source)
    with pytest.raises(BatchInterruptedError) as caught:
        prospector_engine.ProspectorEngine(EngineConfig()).search_many(requests("A", "B", "C"))
    error = caught.value
    assert seen == ["A", "B"]
    assert len(error.completed.entries) == 1
    assert error.completed.entries[0].request.query.keyword == "A"
    assert error.interrupted_query_index == 1
    assert error.remaining_query_indices == (2,)
    assert error.reason_code == reason
    assert "programming defect" not in str(error)


def test_cleanup_failure_on_controlled_error_is_critical(monkeypatch):
    seen = []

    def source(query, limit, **kwargs):
        seen.append(query.keyword)
        error = ProspectorNavigationError("navigation failed")
        error._prospector_cleanup_failed = True
        raise error

    monkeypatch.setattr(prospector_engine, "_run_google_maps", source)
    with pytest.raises(BatchInterruptedError) as caught:
        prospector_engine.ProspectorEngine(EngineConfig()).search_many(requests("A", "B"))
    assert seen == ["A"]
    assert caught.value.reason_code == "cleanup_failed"
    assert caught.value.completed.entries == []
    assert caught.value.remaining_query_indices == (1,)


def test_structural_sidecar_failure_never_continues(monkeypatch):
    seen = []

    def source(query, limit, **kwargs):
        seen.append(query.keyword)
        return _SourceResult(query, [Business("Cafe")])

    monkeypatch.setattr(prospector_engine, "_run_google_maps", source)
    with pytest.raises(BatchInterruptedError) as caught:
        prospector_engine.ProspectorEngine(EngineConfig()).search_many(requests("A", "B"))
    assert seen == ["A"]
    assert caught.value.completed.entries == []


def test_invalid_late_request_rejected_before_first_source_call(monkeypatch):
    monkeypatch.setattr(
        prospector_engine, "_run_google_maps",
        lambda *args, **kwargs: pytest.fail("source called before full preflight"),
    )
    invalid = requests("A", "B")
    invalid[1] = replace(invalid[1], limit=True)
    with pytest.raises(Exception, match="limit"):
        prospector_engine.ProspectorEngine(EngineConfig()).search_many(invalid)

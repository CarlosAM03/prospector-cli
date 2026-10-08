"""Neutral observer checks; no public network or Rich renderer required."""

from dataclasses import replace
from pathlib import Path

from engines import prospector_engine
from engines._observability import ExecutionEvent, emit, observe_execution
from engines.config import EngineConfig
from engines.errors import ProspectorExtractionError
from engines.prospector_engine import ProspectorEngine
from models.batch import BatchQuery
from models.business import Business
from models.search_query import SearchQuery, Source
from models.source_identity import SourceIdentityEvidence
from scraper.google_maps.scraper import _SourceResult
import pytest


def _query():
    return SearchQuery(Source.GOOGLE_MAPS, "cafe", "Tijuana")


def _source(query, limit, **kwargs):
    return _SourceResult(
        query, [Business(" cafe ", phone="12345")], identities=[
            SourceIdentityEvidence.unverified(),
        ],
    )


def test_noop_and_failing_observer_leave_source_result_unchanged(monkeypatch):
    monkeypatch.setattr(prospector_engine, "_run_google_maps", _source)
    engine = ProspectorEngine(EngineConfig(limit=1))
    baseline = engine.search(_query())

    def bad_observer(event):
        raise RuntimeError("presentation failure")

    with observe_execution(bad_observer):
        observed = engine.search(_query())
    assert observed.businesses == baseline.businesses
    assert observed.original_businesses == baseline.original_businesses
    assert observed.issues == baseline.issues
    assert observed.total_found == baseline.total_found


def test_single_emits_neutral_stages_metrics_and_recoverable_issue(monkeypatch):
    monkeypatch.setattr(prospector_engine, "_run_google_maps", _source)
    events = []
    with observe_execution(events.append):
        result = ProspectorEngine(EngineConfig(limit=1)).search(_query())
    assert result.total_found == 1
    assert events[0] == ExecutionEvent("execution_started", "query")
    assert events[-1] == ExecutionEvent("execution_completed", "query")
    assert ExecutionEvent("stage_started", "normalization") in events
    assert ExecutionEvent("stage_completed", "normalization") in events
    metrics = {event.name: event.value for event in events if event.kind == "metric_updated"}
    assert metrics["businesses_extracted"] == 1
    assert metrics["businesses_normalized"] == 1
    assert metrics["recoverable_issue_count"] == 1
    assert metrics["query_execution_seconds"] >= 0
    assert ExecutionEvent("recoverable_issue_observed", "normalization", "field_unverifiable") in events


def test_batch_observer_preserves_selection_and_emits_counts(monkeypatch):
    monkeypatch.setattr(prospector_engine, "_run_google_maps", _source)
    engine = ProspectorEngine(EngineConfig(limit=1))
    requests = [BatchQuery(_query(), 1), BatchQuery(replace(_query(), keyword="tea"), 1)]
    baseline = engine.search_many(requests)
    events = []
    with observe_execution(events.append):
        observed = engine.search_many(requests)
    assert [entry.export_indices for entry in observed.entries] == [
        entry.export_indices for entry in baseline.entries
    ]
    assert [entry.status for entry in observed.entries] == [entry.status for entry in baseline.entries]
    assert observed.total_exportable == baseline.total_exportable == 2
    assert [event.value for event in events if event.name == "unverified_identities"] == [1, 1]
    assert [event.value for event in events if event.name == "duplicates_suppressed"] == [0, 0]
    assert events[-1] == ExecutionEvent("execution_completed", "batch")


def test_observer_scope_resets_and_rich_stays_in_presentation():
    events = []
    with observe_execution(events.append):
        emit(ExecutionEvent("stage_started", "feed"))
    emit(ExecutionEvent("stage_completed", "feed"))
    assert events == [ExecutionEvent("stage_started", "feed")]
    src = Path(__file__).parents[2] / "src"
    for layer in ("engines", "scraper", "models"):
        for path in (src / layer).rglob("*.py"):
            assert "import rich" not in path.read_text(encoding="utf-8").lower()
            assert "from rich" not in path.read_text(encoding="utf-8").lower()


def test_controlled_source_failure_emits_failure_without_hiding_error(monkeypatch):
    def failing_source(*args, **kwargs):
        raise ProspectorExtractionError("controlled source failure")

    monkeypatch.setattr(prospector_engine, "_run_google_maps", failing_source)
    events = []
    with observe_execution(events.append):
        with pytest.raises(ProspectorExtractionError, match="controlled source failure"):
            ProspectorEngine(EngineConfig(limit=1)).search(_query())
    assert events[-1] == ExecutionEvent("execution_failed", "query")

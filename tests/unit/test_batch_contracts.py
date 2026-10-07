"""P91 public contracts and pre-browser request validation."""

from dataclasses import FrozenInstanceError

import pytest

from engines.config import EngineConfig
from engines.errors import BatchInterruptedError, ProspectorConfigurationError, ProspectorSourceError
from engines.prospector_engine import ProspectorEngine
from models import (
    BatchQuery, BatchQueryResult, BatchSearchResult, ObservationDisposition,
    ObservationProvenance, ObservationRef, QueryFailure, QueryStatus,
    VerifiedSourceIdentity,
)
from models.business import Business
from models.normalized_business import NormalizedBusiness
from models.search_query import SearchQuery, Source
from models.search_result import SearchResult


def request(limit=50, *, keyword="cafes", source=Source.GOOGLE_MAPS):
    return BatchQuery(SearchQuery(source, keyword, "Tijuana"), limit)


@pytest.mark.parametrize("count", [1, 5])
def test_preflight_accepts_minimum_and_maximum_without_touching_input(count):
    queries = [request(keyword=f"q{i}") for i in range(count)]
    engine = ProspectorEngine(EngineConfig(limit=50))
    snapshot = engine._preflight_batch(queries)
    assert len(snapshot) == count
    assert [entry.query.keyword for entry in snapshot] == [f"q{i}" for i in range(count)]
    assert all(snapshot[index].query is not queries[index].query for index in range(count))
    assert engine.config.limit == 50


@pytest.mark.parametrize("queries", [[], [request()] * 6, None, "q", {request().query.keyword}, {"a": request()}, (item for item in [request()])])
def test_preflight_rejects_unordered_or_wrong_cardinality_before_source(queries, monkeypatch):
    monkeypatch.setattr("engines.prospector_engine._run_google_maps", lambda *args, **kwargs: pytest.fail("source called"))
    with pytest.raises(ProspectorConfigurationError):
        ProspectorEngine(EngineConfig())._preflight_batch(queries)


@pytest.mark.parametrize("bad", [0, 101, True, 1.5, "5", None])
def test_preflight_rejects_invalid_request_limits(bad):
    with pytest.raises(ProspectorConfigurationError):
        ProspectorEngine(EngineConfig())._preflight_batch([request(bad)])


def test_preflight_accepts_100_and_keeps_identical_queries_separate():
    source = request(100)
    snapshot = ProspectorEngine(EngineConfig())._preflight_batch([source, source])
    assert len(snapshot) == 2
    assert snapshot[0] is not snapshot[1]
    assert snapshot[0].query is not snapshot[1].query
    assert snapshot[0].limit == snapshot[1].limit == 100


@pytest.mark.parametrize("bad", [object(), SearchQuery(Source.GOOGLE_MAPS, "x", "y"), BatchQuery("wrong", 1)])
def test_preflight_rejects_invalid_request_types(bad):
    with pytest.raises(ProspectorConfigurationError):
        ProspectorEngine(EngineConfig())._preflight_batch([bad])


def test_preflight_rejects_source_and_invalid_text_types():
    engine = ProspectorEngine(EngineConfig())
    with pytest.raises(ProspectorSourceError):
        engine._preflight_batch([request(source="google_maps")])
    with pytest.raises(ProspectorConfigurationError):
        engine._preflight_batch([BatchQuery(SearchQuery(Source.GOOGLE_MAPS, 7, "Tijuana"), 1)])


def test_preflight_snapshots_mutable_queries_and_does_not_mutate_config():
    original = request(7)
    engine = ProspectorEngine(EngineConfig(limit=50, headless=True))
    snapshot = engine._preflight_batch([original])
    original.query.keyword = "changed"
    original.query.location = "changed"
    original.query.source = "changed"
    assert (snapshot[0].query.source, snapshot[0].query.keyword, snapshot[0].query.location) == (
        Source.GOOGLE_MAPS, "cafes", "Tijuana",
    )
    assert engine.config == EngineConfig(limit=50, headless=True)
    with pytest.raises(FrozenInstanceError):
        original.limit = 4


def test_batch_result_derives_counts_and_rejects_invalid_classifications():
    query = request()
    result = SearchResult(
        query.query,
        businesses=[NormalizedBusiness("A"), NormalizedBusiness("B")],
        original_businesses=[Business("A"), Business("B")],
    )
    observations = (
        ObservationProvenance(ObservationRef(0, 0), None, ObservationDisposition.IDENTITY_UNVERIFIED_EXPORTED),
        ObservationProvenance(ObservationRef(0, 1), None, ObservationDisposition.IDENTITY_UNVERIFIED_EXPORTED),
    )
    valid = BatchQueryResult(query, QueryStatus.SUCCESS, result, export_indices=[0, 1],
                             unverified_identity_indices=[0, 1], observations=observations)
    failed = BatchQueryResult(query, QueryStatus.FAILED, error=QueryFailure("navigation", "Safe."))
    batch = BatchSearchResult([valid, failed], 1.2)
    assert (batch.total_observations, batch.total_exportable,
            batch.duplicates_suppressed, batch.total_unverified) == (2, 2, 0, 2)
    assert failed.observed_count == 0 and failed.exportable_count == 0
    with pytest.raises(ValueError):
        BatchQueryResult(query, QueryStatus.SUCCESS, result, export_indices=[0, 0])
    with pytest.raises(ValueError):
        BatchQueryResult(query, QueryStatus.SUCCESS, result, export_indices=[0, 2])
    with pytest.raises(ValueError):
        BatchQueryResult(query, QueryStatus.FAILED, result=result, error=QueryFailure("x", "Safe."))


def test_interruption_contract_identifies_safe_prefix_and_unstarted_queries():
    completed = BatchSearchResult()
    error = BatchInterruptedError(
        completed=completed, interrupted_query_index=1,
        reason_code="cleanup_failed", remaining_query_indices=(2, 3),
    )
    assert error.completed is completed
    assert error.interrupted_query_index == 1
    assert error.remaining_query_indices == (2, 3)
    assert "cleanup_failed" not in str(error)


def test_identity_value_is_namespaced_but_does_not_certify_a_token():
    first = VerifiedSourceIdentity(Source.GOOGLE_MAPS, "kind-a", "value")
    second = VerifiedSourceIdentity(Source.GOOGLE_MAPS, "kind-b", "value")
    assert first != second
    with pytest.raises(ValueError):
        VerifiedSourceIdentity(Source.GOOGLE_MAPS, "", "value")

"""P94 batch selection at the Engine boundary, with offline source evidence."""

from engines import prospector_engine
from engines.config import EngineConfig
from engines.errors import BatchInterruptedError, ProspectorNavigationError
from models.batch import BatchQuery, QueryStatus, ObservationRef
from models.business import Business
from models.search_issue import SearchIssue
from models.search_query import SearchQuery, Source
from models.source_identity import (
    SourceIdentityEvidence, VerificationState, VerifiedSourceIdentity,
)
from scraper.google_maps.scraper import _SourceResult
import pytest


def query(keyword):
    return BatchQuery(SearchQuery(Source.GOOGLE_MAPS, keyword, "Tijuana"), 75)


def verified(value):
    return SourceIdentityEvidence(
        VerifiedSourceIdentity(Source.GOOGLE_MAPS, "google_place_id", value),
        VerificationState.VERIFIED, "place_id_verified",
    )


def test_abc_engine_selects_exact_cross_query_ids_without_extra_extraction(monkeypatch):
    ids = {"A": ["1", "2", "3"], "B": ["2", "4", "5"], "C": ["1", "5", "6"]}
    calls = []

    def source(request, limit, **kwargs):
        calls.append((request.keyword, limit))
        values = ids[request.keyword]
        return _SourceResult(
            request, [Business(f" {value} ") for value in values],
            identities=[verified(value) for value in values],
        )

    monkeypatch.setattr(prospector_engine, "_run_google_maps", source)
    engine = prospector_engine.ProspectorEngine(EngineConfig(limit=50))
    result = engine.search_many([query("A"), query("B"), query("C")])
    assert calls == [("A", 75), ("B", 75), ("C", 75)]
    assert [entry.export_indices for entry in result.entries] == [[0, 1, 2], [1, 2], [2]]
    assert result.total_observations == 9
    assert result.total_exportable == 6
    assert result.duplicates_suppressed == 3
    assert result.entries[2].suppressed[0].winner == ObservationRef(0, 0)
    assert result.entries[2].suppressed[1].winner == ObservationRef(1, 2)
    assert [entry.result.total_found for entry in result.entries] == [3, 3, 3]
    assert result.entries[1].result.original_businesses[0].name == " 2 "
    assert result.entries[1].result.businesses[0].name == "2"
    assert engine.config.limit == 50


def test_partial_winner_failed_query_and_unverified_are_conservative(monkeypatch):
    def source(request, limit, **kwargs):
        if request.keyword == "B":
            raise ProspectorNavigationError("hidden detail")
        if request.keyword == "A":
            return _SourceResult(
                request, [Business("A"), Business("Unknown")],
                issues=[SearchIssue("feed", "partial_results", "Safe.")],
                identities=[verified("branch-one"), SourceIdentityEvidence.unverified()],
            )
        return _SourceResult(
            request, [Business("A Again"), Business("Unknown Again")],
            identities=[verified("branch-one"), SourceIdentityEvidence.unverified()],
        )

    monkeypatch.setattr(prospector_engine, "_run_google_maps", source)
    result = prospector_engine.ProspectorEngine(EngineConfig()).search_many(
        [query("A"), query("B"), query("C")],
    )
    assert [item.status for item in result.entries] == [
        QueryStatus.PARTIAL, QueryStatus.FAILED, QueryStatus.SUCCESS,
    ]
    assert result.entries[1].result is None
    assert result.entries[2].export_indices == [1]
    assert result.entries[2].unverified_identity_indices == [1]
    assert result.entries[2].suppressed[0].winner == ObservationRef(0, 0)
    assert result.total_observations == 4
    assert result.total_exportable == 3


def test_identity_index_does_not_persist_between_search_many_calls(monkeypatch):
    monkeypatch.setattr(
        prospector_engine, "_run_google_maps",
        lambda request, limit, **kwargs: _SourceResult(
            request, [Business("A")], identities=[verified("same")],
        ),
    )
    engine = prospector_engine.ProspectorEngine(EngineConfig())
    first = engine.search_many([query("A")])
    second = engine.search_many([query("B")])
    assert first.entries[0].export_indices == [0]
    assert second.entries[0].export_indices == [0]


def test_selection_invariant_failure_keeps_only_previously_completed_prefix(monkeypatch):
    monkeypatch.setattr(
        prospector_engine, "_run_google_maps",
        lambda request, limit, **kwargs: _SourceResult(
            request, [Business(request.keyword)], identities=[verified(request.keyword)],
        ),
    )
    real_select = prospector_engine.select_batch_exports

    def broken_selection(batch):
        if len(batch.entries) == 2:
            raise ValueError("invalid provenance")
        return real_select(batch)

    monkeypatch.setattr(prospector_engine, "select_batch_exports", broken_selection)
    with pytest.raises(BatchInterruptedError) as caught:
        prospector_engine.ProspectorEngine(EngineConfig()).search_many(
            [query("A"), query("B"), query("C")],
        )
    assert [entry.request.query.keyword for entry in caught.value.completed.entries] == ["A"]
    assert caught.value.interrupted_query_index == 1
    assert caught.value.remaining_query_indices == (2,)


def test_datra_style_sectors_with_branches_homonyms_incomplete_and_no_history(monkeypatch):
    """Synthetic scenario: only observed verified place IDs participate."""
    historic_csv = {"same-name.example", "old campaign phone"}
    scenarios = {
        "manufacturing": [
            ("ACME PLANT", verified("plant-north")),
            ("CAFÉ RÍO", SourceIdentityEvidence.unverified()),
            ("CHAIN SHOP", verified("branch-west")),
        ],
        "suppliers": [
            ("ACME PLANT, more details", verified("plant-north")),
            ("CHAIN SHOP", verified("branch-east")),
            ("CAFÉ RÍO", SourceIdentityEvidence.unverified()),
        ],
        "services": [
            ("CHAIN SHOP", verified("branch-west")),
            ("UNNAMED", SourceIdentityEvidence.unverified()),
        ],
    }

    def source(request, limit, **kwargs):
        observed = scenarios[request.keyword]
        return _SourceResult(
            request, [Business(name) for name, _ in observed],
            identities=[evidence for _, evidence in observed],
        )

    monkeypatch.setattr(prospector_engine, "_run_google_maps", source)
    batch = prospector_engine.ProspectorEngine(EngineConfig()).search_many([
        query("manufacturing"), query("suppliers"), query("services"),
    ])
    assert [entry.export_indices for entry in batch.entries] == [[0, 1, 2], [1, 2], [1]]
    assert batch.total_observations == 8
    assert batch.total_exportable == 6
    assert batch.duplicates_suppressed == 2
    assert batch.entries[1].result.original_businesses[0].name == "ACME PLANT, more details"
    assert historic_csv  # It is deliberately never passed to the Engine.

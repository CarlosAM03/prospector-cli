"""Controlled global execution without external source or network calls."""

from dataclasses import replace

import pytest

from engines.config import EngineConfig
from engines.normalization import NormalizationEngine
from engines.prospector_engine import ProspectorEngine
from models.business import Business
from models.normalized_business import NormalizedBusiness
from models.search_issue import SearchIssue
from models.search_query import SearchQuery, Source
from models.search_result import SearchResult
from models.source_identity import SourceIdentityEvidence
from scraper.google_maps import scraper
from scraper.google_maps.scraper import _SourceResult
from engines import prospector_engine


def query():
    return SearchQuery(Source.GOOGLE_MAPS, "cafes", "Tijuana")


def unverified(count):
    return [SourceIdentityEvidence.unverified() for _ in range(count)]


def test_engine_and_wrapper_use_same_single_normalization(monkeypatch):
    original = Business(
        "  Hospital   Excel ", category=" Hospital privado ",
        phone="(664) 123-4567", email="INFO@EXAMPLE.TEST",
        website=" https://Example.test/Path?X=1 ", language="es-MX",
    )
    calls = []
    normalized_calls = []
    real_normalize = NormalizationEngine.normalize_businesses

    def source(*args, **kwargs):
        calls.append((args, kwargs))
        return _SourceResult(args[0], [replace(original)], 0.01, [
            SearchIssue("feed", "partial_results", "Safe."),
        ], unverified(1))

    def count_normalize(self, businesses, **kwargs):
        normalized_calls.append(len(businesses))
        return real_normalize(self, businesses, **kwargs)

    monkeypatch.setattr(NormalizationEngine, "normalize_businesses", count_normalize)
    monkeypatch.setattr(prospector_engine, "_run_google_maps", source)
    monkeypatch.setattr(scraper, "_run_google_maps", source)
    engine_result = ProspectorEngine(EngineConfig(limit=2)).search(query())
    wrapper_result = scraper.search_businesses(query(), 2)

    for result in (engine_result, wrapper_result):
        assert isinstance(result.businesses[0], NormalizedBusiness)
        assert isinstance(result.original_businesses[0], Business)
        assert result.businesses[0].name == "HOSPITAL EXCEL"
        assert result.businesses[0].category == "HOSPITAL PRIVADO"
        assert result.businesses[0].phone == "664 123 4567"
        assert result.businesses[0].email == "info@example.test"
        assert result.businesses[0].website == "https://Example.test/Path?X=1"
        assert result.businesses[0].language == "ES-MX"
        assert result.original_businesses[0].name == original.name
        assert result.issues[0].stage == "feed"
        assert result.total_found == 1
        assert result.execution_time >= 0
    assert normalized_calls == [1, 1]
    assert len(calls) == 2
    assert calls[0][1]["typed_errors"] is True
    assert "typed_errors" not in calls[1][1]


def test_legacy_limits_are_passed_through_without_engine_policy(monkeypatch):
    seen = []

    def source(q, limit, **kwargs):
        seen.append(limit)
        return _SourceResult(q)

    monkeypatch.setattr(scraper, "_run_google_maps", source)
    for limit in (0, 101):
        result = scraper.search_businesses(query(), limit)
        assert result.businesses == result.original_businesses == []
    assert seen == [0, 101]


def test_controlled_hundred_results_keep_order_and_count(monkeypatch):
    originals = [Business(f" Cafe {index} ") for index in range(100)]
    monkeypatch.setattr(
        prospector_engine, "_run_google_maps",
        lambda q, limit, **kwargs: _SourceResult(
            q, originals[:limit], identities=unverified(limit),
        ),
    )
    result = ProspectorEngine(EngineConfig(limit=100)).search(query())
    assert result.total_found == 100
    assert len(result.original_businesses) == 100
    assert [item.name for item in result.businesses] == [
        f"CAFE {index}" for index in range(100)
    ]
    assert [item.name for item in originals] == [
        f" Cafe {index} " for index in range(100)
    ]


def test_normalization_issue_follows_existing_issue(monkeypatch):
    def source(q, limit, **kwargs):
        return _SourceResult(q, [Business(" cafe ", phone="12345")], issues=[
            SearchIssue("website", "inspection_unavailable", "Safe."),
        ], identities=unverified(1))

    monkeypatch.setattr(prospector_engine, "_run_google_maps", source)
    result = ProspectorEngine(EngineConfig(limit=1)).search(query())
    assert [issue.stage for issue in result.issues] == ["website", "normalization"]
    assert result.issues[1].candidate == "business[0].phone"
    assert result.businesses[0].name == "CAFE"
    assert result.businesses[0].phone == result.original_businesses[0].phone


def test_unexpected_normalization_error_is_not_hidden(monkeypatch):
    monkeypatch.setattr(
        prospector_engine, "_run_google_maps",
        lambda q, limit, **kwargs: _SourceResult(
            q, [Business("Cafe")], identities=unverified(1),
        ),
    )
    def broken(self, businesses, **kwargs):
        raise RuntimeError("normalizer defect")
    monkeypatch.setattr(NormalizationEngine, "normalize_businesses", broken)
    with pytest.raises(RuntimeError, match="normalizer defect"):
        ProspectorEngine(EngineConfig(limit=1)).search(query())

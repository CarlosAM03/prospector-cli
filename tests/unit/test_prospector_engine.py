"""Controlled facade checks without endorsing an Engine capacity value."""

import pytest

from engines import prospector_engine
from engines.config import EngineConfig
from models.search_query import SearchQuery, Source
from models.search_result import SearchResult


def test_facade_delegates_config_and_preserves_result(monkeypatch):
    query = SearchQuery(Source.GOOGLE_MAPS, "cafes", "Tijuana")
    expected = SearchResult(query)
    calls = []
    monkeypatch.setattr(prospector_engine.ProspectorEngine, "ENGINE_MAX_LIMIT", 8)
    monkeypatch.setattr(
        prospector_engine, "_run_google_maps",
        lambda *args, **kwargs: calls.append((args, kwargs)) or expected,
    )
    config = EngineConfig(limit=7, headless=True, website_enrichment=False)
    actual = prospector_engine.ProspectorEngine(config).search(query)
    assert actual is expected
    assert calls == [((query, 7), {"headless": True, "website_enrichment": False})]


def test_facade_rejects_unapproved_maximum_before_source_io(monkeypatch):
    query = SearchQuery(Source.GOOGLE_MAPS, "cafes", "Tijuana")
    monkeypatch.setattr(
        prospector_engine, "_run_google_maps",
        lambda *args, **kwargs: pytest.fail("source I/O before policy validation"),
    )
    with pytest.raises(RuntimeError, match="not been approved"):
        prospector_engine.ProspectorEngine(EngineConfig()).search(query)


def test_facade_rejects_over_maximum_without_clamping(monkeypatch):
    monkeypatch.setattr(prospector_engine.ProspectorEngine, "ENGINE_MAX_LIMIT", 8)
    query = SearchQuery(Source.GOOGLE_MAPS, "cafes", "Tijuana")
    with pytest.raises(ValueError, match="9 exceeds engine maximum 8"):
        prospector_engine.ProspectorEngine(EngineConfig(limit=9)).search(query)


def test_facade_rejects_unsupported_source_before_runtime(monkeypatch):
    query = SearchQuery("unknown", "cafes", "Tijuana")
    with pytest.raises(NotImplementedError, match="unsupported source"):
        prospector_engine.ProspectorEngine(EngineConfig()).search(query)

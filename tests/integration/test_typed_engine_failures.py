"""Typed fatal boundaries preserve causes and runtime cleanup offline."""

import pytest
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from engines.config import EngineConfig
from engines.errors import (
    ProspectorExtractionError,
    ProspectorNavigationError,
    ProspectorRuntimeError,
)
from engines.prospector_engine import ProspectorEngine
from models.search_query import SearchQuery, Source
from scraper.google_maps import scraper


class Runtime:
    def __init__(self):
        self.browser = self
        self.closes = 0

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.closes += 1

    def new_page(self):
        return object()


def run(monkeypatch):
    runtime = Runtime()
    monkeypatch.setattr(scraper, "BrowserRuntime", lambda **kwargs: runtime)
    monkeypatch.setattr(ProspectorEngine, "ENGINE_MAX_LIMIT", 10)
    query = SearchQuery(Source.GOOGLE_MAPS, "cafes", "Tijuana")
    return runtime, ProspectorEngine(EngineConfig(limit=3)), query


def test_navigation_failure_is_typed_chained_and_cleans_up(monkeypatch):
    runtime, engine, query = run(monkeypatch)
    def fail(*args, **kwargs):
        raise PlaywrightTimeoutError("browser internals")
    monkeypatch.setattr(scraper, "create_search_page", fail)
    with pytest.raises(ProspectorNavigationError) as caught:
        engine.search(query)
    assert isinstance(caught.value.__cause__, PlaywrightTimeoutError)
    assert "browser internals" not in str(caught.value)
    assert runtime.closes == 1


def test_ambiguous_feed_failure_is_typed_chained_and_cleans_up(monkeypatch):
    runtime, engine, query = run(monkeypatch)
    monkeypatch.setattr(scraper, "create_search_page", lambda *a, **k: object())
    def fail(*args, **kwargs):
        raise LookupError("feed not verifiable")
    monkeypatch.setattr(scraper, "extract_businesses", fail)
    with pytest.raises(ProspectorExtractionError) as caught:
        engine.search(query)
    assert isinstance(caught.value.__cause__, LookupError)
    assert runtime.closes == 1


def test_runtime_start_failure_is_typed_without_hiding_cause(monkeypatch):
    _, engine, query = run(monkeypatch)
    def fail(**kwargs):
        raise OSError("internal launch detail")
    monkeypatch.setattr(scraper, "BrowserRuntime", fail)
    with pytest.raises(ProspectorRuntimeError) as caught:
        engine.search(query)
    assert isinstance(caught.value.__cause__, OSError)
    assert "internal launch detail" not in str(caught.value)


def test_unexpected_programming_error_is_not_misclassified(monkeypatch):
    runtime, engine, query = run(monkeypatch)
    monkeypatch.setattr(scraper, "create_search_page", lambda *a, **k: object())
    def fail(*args, **kwargs):
        raise TypeError("programming error")
    monkeypatch.setattr(scraper, "extract_businesses", fail)
    with pytest.raises(TypeError, match="programming error"):
        engine.search(query)
    assert runtime.closes == 1

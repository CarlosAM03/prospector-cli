"""Controlled CLI migration and legacy wrapper compatibility."""

import pytest

from models.search_issue import SearchIssue
from models.business import Business
from models.normalized_business import NormalizedBusiness
from models.search_query import SearchQuery, Source
from models.search_result import SearchResult
from scraper.google_maps.scraper import _SourceResult
from scraper.google_maps import scraper
import main as cli


@pytest.mark.parametrize("typed_limit,expected", [("", 50), ("1", 1), ("50", 50), ("100", 100)])
def test_cli_uses_engine_with_default_or_explicit_limit(
    monkeypatch, capsys, typed_limit, expected
):
    answers = iter(["cafes", "Tijuana", typed_limit, "3"])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(answers))
    called = []

    class FakeEngine:
        def __init__(self, config):
            called.append(config)

        def search(self, query):
            called.append(query)
            result = SearchResult(query)
            result.issues.append(SearchIssue(
                "feed", "partial_results", "Available businesses were preserved."
            ))
            return result

    monkeypatch.setattr(cli, "ProspectorEngine", FakeEngine)
    cli.execute_search()
    assert called[0].limit == expected
    assert (called[1].keyword, called[1].location) == ("cafes", "Tijuana")
    output = capsys.readouterr().out
    assert "Businesses Found : 0" in output
    assert "Recoverable Issues: 1" in output
    assert "feed/partial_results" in output


@pytest.mark.parametrize("typed_limit", ["0", "-1", "abc", "1.5"])
def test_cli_rejects_invalid_limit_before_engine(monkeypatch, capsys, typed_limit):
    answers = iter(["cafes", "Tijuana", typed_limit])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(answers))
    monkeypatch.setattr(cli, "ProspectorEngine", lambda config: pytest.fail(
        "Engine constructed for invalid input"
    ))
    cli.execute_search()
    assert "Limit must be a positive whole number" in capsys.readouterr().out


def test_cli_rejects_101_before_engine_or_browser(monkeypatch, capsys):
    answers = iter(["cafes", "Tijuana", "101"])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(answers))
    monkeypatch.setattr(cli, "ProspectorEngine", lambda config: pytest.fail(
        "Engine constructed before limit validation"
    ))
    cli.execute_search()
    assert "maximum permitted limit is 100" in capsys.readouterr().out


def test_legacy_wrapper_keeps_programmatic_default_and_unclamped_value(monkeypatch):
    query = SearchQuery(Source.GOOGLE_MAPS, "cafes", "Tijuana")
    observed = []
    monkeypatch.setattr(
        scraper, "_run_google_maps",
        lambda *args, **kwargs: observed.append((args, kwargs)) or _SourceResult(query),
    )
    scraper.search_businesses(query)
    scraper.search_businesses(query, 0)
    assert [args[1] for args, _ in observed] == [50, 0]
    assert all(kwargs == {
        "headless": False, "website_enrichment": True
    } for _, kwargs in observed)


def test_cli_displays_normalized_view_and_safe_issue_context(monkeypatch, capsys):
    answers = iter(["cafes", "Tijuana", "", "3"])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(answers))

    class FakeEngine:
        def __init__(self, config):
            assert config.limit == 50

        def search(self, query):
            return SearchResult(
                query,
                businesses=[NormalizedBusiness(
                    name="CAFE RÍO", category="CAFÉ",
                    address="Av. Río 1", phone="664 123 4567",
                    email="info@example.test",
                    website="https://Example.test/Path", language="ES-MX",
                )],
                original_businesses=[Business(
                    name="Cafe Río", category="Café", phone="(664) 123-4567",
                )],
                issues=[SearchIssue(
                    "normalization", "field_unverifiable",
                    "A business field could not be normalized safely; its original value was preserved.",
                    candidate="business[0].phone",
                )],
            )

    monkeypatch.setattr(cli, "ProspectorEngine", FakeEngine)
    cli.execute_search()
    output = capsys.readouterr().out
    assert "[1] CAFE RÍO" in output
    assert "Category : CAFÉ" in output
    assert "Phone    : 664 123 4567" in output
    assert "Language : ES-MX" in output
    assert "normalization/field_unverifiable (business[0].phone)" in output
    assert "(664) 123-4567" not in output

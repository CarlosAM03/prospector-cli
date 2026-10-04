"""Offline orchestration and cleanup checks for the current Maps boundary."""

import csv

import pytest

from models.business import Business
from engines._issue_draft import _IssueCollector
from models.search_query import SearchQuery, Source
from scraper.google_maps import scraper
from services.export_service import ExportFormat, ExportService


class Browser:
    def __init__(self):
        self.closes = 0
        self.headless = None

    def close(self):
        self.closes += 1


class Runtime:
    def __init__(self, browser, page, headless):
        self.browser = browser
        self.page = page
        browser.headless = headless

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.browser.close()

    def new_page(self):
        return self.page


def setup(monkeypatch, records=None, failure=None):
    browser = Browser()
    page = object()
    monkeypatch.setattr(
        scraper, "BrowserRuntime",
        lambda *, headless: Runtime(browser, page, headless),
    )
    def open_page(*args, **kwargs):
        if failure == "navigation":
            raise RuntimeError("navigation failed")
        assert kwargs["page_factory"]() is page
        return page
    def extract(*args, **kwargs):
        if failure == "feed":
            raise LookupError("indeterminate feed")
        return records if records is not None else []
    monkeypatch.setattr(scraper, "create_search_page", open_page)
    monkeypatch.setattr(scraper, "extract_businesses", extract)
    monkeypatch.setattr(scraper, "enrich_business", lambda **kwargs: kwargs["business"])
    monkeypatch.setattr(scraper, "enrich_websites", lambda **kwargs: kwargs["businesses"])
    query = SearchQuery(Source.GOOGLE_MAPS, "cafes", "Tijuana")
    return browser, query


def record(name, key):
    return {"href": f"/maps/place/{name}/data=!1s{key}!",
            "identity": {"name": name}, "business": Business(name=name)}


def test_t_i01_fatal_navigation_closes_and_optional_partial_survives(monkeypatch):
    browser, query = setup(monkeypatch, failure="navigation")
    with pytest.raises(RuntimeError, match="navigation failed"):
        scraper.search_businesses(query, 2)
    assert browser.closes == 1

    browser, query = setup(monkeypatch, [record("Cafe", "1")])
    result = scraper.search_businesses(query, 2)
    assert result.businesses[0].name == "Cafe" and browser.closes == 1


def test_t_i02_order_limit_query_and_total_found(monkeypatch):
    browser, query = setup(monkeypatch, [record("A", "1"), record("B", "2")])
    result = scraper.search_businesses(query, 2)
    assert result.query is query
    assert [b.name for b in result.businesses] == ["A", "B"]
    assert result.total_found == 2 and result.execution_time >= 0
    assert browser.closes == 1


def test_t_i03_partial_result_still_exports_legacy_schema(monkeypatch, tmp_path):
    _, query = setup(monkeypatch, [record("A", "1")])
    result = scraper.search_businesses(query, 2)
    monkeypatch.chdir(tmp_path)
    path = ExportService.export(result, ExportFormat.CSV)
    with open(path, newline="", encoding="utf-8") as stream:
        rows = list(csv.reader(stream))
    assert rows[0] == ["Name", "Category", "Address", "Phone", "Email", "Website", "Language"]
    assert len(rows) == 2 and rows[1][0] == "A"


def test_t_i05_stalled_feed_with_or_without_valid_business(monkeypatch):
    browser, query = setup(monkeypatch, [record("A", "1")])
    assert scraper.search_businesses(query, 5).total_found == 1
    assert browser.closes == 1
    browser, query = setup(monkeypatch, failure="feed")
    with pytest.raises(LookupError, match="indeterminate"):
        scraper.search_businesses(query, 5)
    assert browser.closes == 1


def test_t_i06_normal_and_fatal_paths_close_once_preserving_exception(monkeypatch):
    browser, query = setup(monkeypatch, [])
    scraper.search_businesses(query, 1)
    assert browser.closes == 1
    browser, query = setup(monkeypatch, failure="navigation")
    with pytest.raises(RuntimeError, match="navigation failed"):
        scraper.search_businesses(query, 1)
    assert browser.closes == 1


def test_private_issue_collector_crosses_pipeline_without_public_schema(monkeypatch):
    _, query = setup(monkeypatch, [record("Cafe", "1")])
    collector = _IssueCollector()
    def inspect(**kwargs):
        kwargs["issue_collector"].record("website", "inspection_unavailable")
        return kwargs["businesses"]
    monkeypatch.setattr(scraper, "enrich_websites", inspect)
    result = scraper._run_google_maps(
        query, 1, headless=True, website_enrichment=True,
        issue_collector=collector,
    )
    assert result.total_found == 1
    assert [(x.stage, x.reason) for x in collector.items] == [
        ("website", "inspection_unavailable")
    ]

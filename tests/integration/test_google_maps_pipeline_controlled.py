"""Offline orchestration and cleanup checks for the current Maps boundary."""

import csv

import pytest

from models.business import Business
from models.normalized_business import NormalizedBusiness
from engines.issue_collector import IssueCollector
from models.search_query import SearchQuery, Source
from models.search_issue import SearchIssue
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
    assert isinstance(result.businesses[0], NormalizedBusiness)
    assert result.businesses[0].name == "CAFE" and browser.closes == 1
    assert result.original_businesses[0].name == "Cafe"


def test_t_i02_order_limit_query_and_total_found(monkeypatch):
    browser, query = setup(monkeypatch, [record("A", "1"), record("B", "2")])
    result = scraper.search_businesses(query, 2)
    assert result.query is query
    assert [b.name for b in result.businesses] == ["A", "B"]
    assert [b.name for b in result.original_businesses] == ["A", "B"]
    assert result.total_found == 2 and result.execution_time >= 0
    assert browser.closes == 1


def test_t_i03_partial_result_still_exports_legacy_schema(monkeypatch, tmp_path):
    _, query = setup(monkeypatch, [record("A", "1")])
    result = scraper.search_businesses(query, 2)
    result.issues.append(SearchIssue("feed", "partial_results", "Safe."))
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


def test_issues_cross_pipeline_into_public_search_result(monkeypatch):
    _, query = setup(monkeypatch, [record("Cafe", "1")])
    collector = IssueCollector()
    def inspect(**kwargs):
        kwargs["issue_collector"].record("website", "inspection_unavailable")
        return kwargs["businesses"]
    monkeypatch.setattr(scraper, "enrich_websites", inspect)
    result = scraper._run_google_maps(
        query, 1, headless=True, website_enrichment=True,
        issue_collector=collector,
    )
    assert result.total_found == 1
    assert [(x.stage, x.code) for x in collector.items] == [
        ("website", "inspection_unavailable")
    ]
    assert result.issues == collector.items


def test_internal_pilot_metrics_do_not_change_result_contract(monkeypatch):
    _, query = setup(monkeypatch, [record("Cafe", "1")])
    metrics = {}
    result = scraper._run_google_maps(
        query, 1, headless=True, website_enrichment=True,
        metrics_sink=metrics,
    )
    assert result.total_found == 1
    assert metrics["observed_candidates"] == 1
    assert metrics["cleanup_completed"] is True
    assert all(metrics[key] >= 0 for key in (
        "navigation_seconds", "feed_seconds", "detail_seconds", "website_seconds"
    ))


def test_address_fragment_category_is_cleared_without_changing_identity(monkeypatch):
    first = record("Baja Border Maquila", "1")
    first["business"].category = "C. Pacifico 9030"
    first["business"].address = "C. Pacifico 9030, Parque Industrial Pacifico II"
    second = record("Another factory", "2")
    second["business"].category = "Fábrica"
    second["business"].address = "C. 5 Sur 155, Tijuana"
    third = record("Unknown address", "3")
    third["business"].category = "Avenida Universidad 102"
    browser, query = setup(monkeypatch, [first, second, third])

    result = scraper.search_businesses(query, 3)

    assert [business.name for business in result.businesses] == [
        "BAJA BORDER MAQUILA", "ANOTHER FACTORY", "UNKNOWN ADDRESS"
    ]
    assert [business.category for business in result.businesses] == [
        None, "FÁBRICA", "AVENIDA UNIVERSIDAD 102"
    ]
    assert [business.name for business in result.original_businesses] == [
        "Baja Border Maquila", "Another factory", "Unknown address"
    ]
    assert result.total_found == 3
    assert browser.closes == 1

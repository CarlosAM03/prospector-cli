"""Provisional internal transport checks; no public issue schema is asserted."""

from engines._issue_draft import _IssueCollector
from models.business import Business
from scraper.google_maps import detail_panel, website_enrichment


def test_detail_skip_records_internal_reason_without_mutation():
    collector = _IssueCollector()
    business = Business(name="Cafe", address="Summary")
    returned = detail_panel.enrich_business(
        None, "/maps/place/Cafe/", business, issue_collector=collector
    )
    assert returned is business and business.address == "Summary"
    assert [(x.stage, x.reason) for x in collector.items] == [
        ("detail", "identity_unverifiable")
    ]


def test_website_failure_records_internal_exception_and_keeps_business(monkeypatch):
    class FailingEngine:
        def __init__(self, browser):
            pass

        def inspect(self, url):
            raise OSError("offline")

    monkeypatch.setattr(website_enrichment, "WebsiteEngine", FailingEngine)
    collector = _IssueCollector()
    business = Business(name="Cafe", website="https://example.test")
    assert website_enrichment.enrich_websites(
        None, [business], issue_collector=collector
    ) == [business]
    assert business.website_title is None
    assert [(x.stage, x.reason, x.exception_type) for x in collector.items] == [
        ("website", "inspection_unavailable", "OSError")
    ]

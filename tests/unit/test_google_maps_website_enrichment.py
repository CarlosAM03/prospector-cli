"""Optional Website Engine failures cannot erase prior Maps data."""

import logging
from types import SimpleNamespace

from models.business import Business
from scraper.google_maps import website_enrichment


def metadata(**overrides):
    data = dict(title="Site", description="Description", language="es",
                has_contact_page=False, has_about_page=False, status_code=200,
                emails=["hello@example.test"])
    data.update(overrides)
    return SimpleNamespace(**data)


def engine(monkeypatch, inspect):
    class FakeEngine:
        def __init__(self, browser):
            pass

        def inspect(self, url):
            return inspect(url)

    monkeypatch.setattr(website_enrichment, "WebsiteEngine", FakeEngine)


def test_t_w01_no_website_skips_inspection(monkeypatch):
    engine(monkeypatch, lambda url: (_ for _ in ()).throw(AssertionError("inspected")))
    business = Business(name="Cafe", address="Maps")
    assert website_enrichment.enrich_websites(None, [business]) == [business]
    assert business.address == "Maps"


def test_t_w02_one_inspection_failure_does_not_block_next(monkeypatch):
    def inspect(url):
        if "bad" in url:
            raise RuntimeError("offline")
        return metadata()
    engine(monkeypatch, inspect)
    first = Business(name="A", address="Maps A", website="https://bad.test")
    second = Business(name="B", address="Maps B", website="https://good.test")
    assert website_enrichment.enrich_websites(None, [first, second]) == [first, second]
    assert first.website_title is None and first.address == "Maps A"
    assert second.website_title == "Site"


def test_t_w03_partial_or_throwing_metadata_is_not_half_applied(monkeypatch):
    class Broken:
        title = "Would leak"
        description = "Would leak"
        language = "es"
        has_contact_page = False
        has_about_page = False
        status_code = 200

        @property
        def emails(self):
            raise RuntimeError("bad property")

    engine(monkeypatch, lambda url: Broken())
    business = Business(name="Cafe", address="Maps", website="https://site.test",
                        website_title="Prior")
    website_enrichment.enrich_websites(None, [business])
    assert business.website_title == "Prior" and business.address == "Maps"


def test_t_w04_success_maps_metadata_without_overwriting_maps(monkeypatch):
    engine(monkeypatch, lambda url: metadata(description=None))
    business = Business(name="Cafe", address="Maps address", phone="123",
                        website="https://site.test", website_description="Prior")
    website_enrichment.enrich_websites(None, [business])
    assert (business.name, business.address, business.phone) == (
        "Cafe", "Maps address", "123"
    )
    assert business.website_description == "Prior"
    assert (business.website_title, business.language, business.email) == (
        "Site", "es", "hello@example.test"
    )


def test_optional_failure_logs_diagnostic_without_changing_result(monkeypatch, caplog, capsys):
    engine(monkeypatch, lambda url: (_ for _ in ()).throw(RuntimeError("offline")))
    business = Business(name="Cafe", website="https://site.test")
    with caplog.at_level(logging.WARNING, logger=website_enrichment.__name__):
        result = website_enrichment.enrich_websites(None, [business])
    assert result == [business] and business.website_title is None
    assert "Website enrichment unavailable" in caplog.text
    assert "RuntimeError" in caplog.text
    assert capsys.readouterr().out == ""

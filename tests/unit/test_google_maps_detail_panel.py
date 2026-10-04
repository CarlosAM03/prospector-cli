"""Controlled identity transitions for Google Maps detail enrichment."""

import pytest

from models.business import Business
from scraper.google_maps import detail_panel


def href(key, name="Cafe"):
    return f"/maps/place/{name}/data=!1s{key}!"


class Field:
    def __init__(self, page, selector):
        self.page = page
        self.selector = selector

    @property
    def last(self):
        return self

    def inner_text(self, timeout=1000):
        if self.selector == "h1":
            value = self.page.state["title"]
        elif "address" in self.selector:
            value = self.page.state.get("address")
        elif "phone" in self.selector:
            value = self.page.state.get("phone")
        else:
            value = None
        if value is None:
            raise LookupError(self.selector)
        return value

    def get_attribute(self, name, timeout=1000):
        return self.page.state.get("website")

    def wait_for(self, **kwargs):
        return None


class Panel:
    def __init__(self, page):
        self.page = page

    def inner_text(self, timeout=1000):
        return self.page.state["text"]

    def locator(self, selector):
        return Field(self.page, selector)


class PanelList:
    def __init__(self, page):
        self.page = page

    @property
    def last(self):
        return Panel(self.page)

    @property
    def first(self):
        return self

    def count(self):
        return int(self.page.state.get("visible", True))

    def is_visible(self):
        return bool(self.page.state.get("visible", True))


class Target:
    def __init__(self, page):
        self.page = page

    def get_attribute(self, name):
        return self.page.target_href

    def click(self, timeout=3000):
        self.page.clicked = True
        self.page.after_click(self.page)


class TargetList:
    def __init__(self, page):
        self.page = page

    def count(self):
        return int(self.page.target_present)

    def nth(self, index):
        return Target(self.page)


class Page:
    def __init__(self, target_href, after_click=None):
        self.target_href = target_href
        self.target_present = True
        self.clicked = False
        self.clock = 0.0
        self.url = "https://www.google.com/maps/place/Old/data=!1sold!"
        self.state = {"title": "Old", "text": "Old panel", "address": "Old address"}
        self.after_click = after_click or valid_transition
        self.on_wait = lambda page: None

    def locator(self, selector):
        if selector.startswith("a["):
            return TargetList(self)
        return PanelList(self)

    def wait_for_timeout(self, ms):
        self.clock += ms / 1000
        self.on_wait(self)


def valid_transition(page):
    page.url = f"https://www.google.com{page.target_href}"
    page.state = {
        "title": "Cafe", "text": "Cafe new panel", "address": "New address",
        "phone": "555 123 4567", "website": "https://example.test",
    }


def run(monkeypatch, page, name="Cafe", business=None):
    monkeypatch.setattr(detail_panel.time, "monotonic", lambda: page.clock)
    business = business or Business(name=name, address="Summary address")
    returned = detail_panel.enrich_business(
        page, page.target_href, business, {"name": name, "href": page.target_href}
    )
    assert returned is business
    return business


def test_t_d01_valid_identity_merges_verified_fields(monkeypatch):
    page = Page(href("target"))
    business = run(monkeypatch, page)
    assert page.clicked
    assert (business.address, business.phone, business.website) == (
        "New address", "555 123 4567", "https://example.test"
    )


def test_t_d02_missing_link_or_stale_panel_keeps_summary(monkeypatch):
    page = Page(href("target"))
    page.target_present = False
    assert run(monkeypatch, page).address == "Summary address"
    page = Page(href("target"), after_click=lambda p: setattr(p, "url", f"https://www.google.com{p.target_href}"))
    assert run(monkeypatch, page).address == "Summary address"


def test_t_d03_place_id_mismatch_and_substring_collision(monkeypatch):
    page = Page(href("target"), after_click=lambda p: setattr(p, "url", "https://x/maps/place/X/data=!1starget-extra!"))
    assert run(monkeypatch, page).address == "Summary address"


def test_t_d04_same_name_cannot_override_wrong_place_id(monkeypatch):
    def wrong(page):
        page.url = "https://x/maps/place/Cafe/data=!1sother!"
        page.state = {"title": "Cafe", "text": "Other Cafe", "address": "Wrong"}
    assert run(monkeypatch, Page(href("target"), wrong)).address == "Summary address"


def test_t_d05_waits_for_coherent_optional_fields(monkeypatch):
    page = Page(href("target"))
    def update(p):
        if p.clock >= 0.1:
            p.state["phone"] = "555 123 4567"
    page.on_wait = update
    business = run(monkeypatch, page)
    assert business.phone == "555 123 4567"


def test_t_d06_missing_optional_fields_preserve_summary(monkeypatch):
    def partial(page):
        page.url = f"https://x{page.target_href}"
        page.state = {"title": "Cafe", "text": "Cafe partial", "address": None,
                      "phone": None, "website": None}
    business = run(monkeypatch, Page(href("target"), partial))
    assert business.address == "Summary address"
    assert business.phone is None


def test_t_d07_identity_change_between_read_and_commit_discards_fields(monkeypatch):
    page = Page(href("target"))
    page.on_wait = lambda p: setattr(p, "url", "https://x/maps/place/Other/data=!1sother!")
    assert run(monkeypatch, page).address == "Summary address"


def test_t_d08_only_whitespace_and_case_equivalence_is_allowed(monkeypatch):
    page = Page(href("target"))
    business = run(monkeypatch, page, name="  caFE   ")
    assert business.address == "New address"


@pytest.mark.parametrize("name", ["Cafe!", "Café", "Cafe and Co"])
def test_t_d09_punctuation_accent_other_changes_are_rejected(monkeypatch, name):
    assert run(monkeypatch, Page(href("target")), name=name).address == "Summary address"


def test_t_d10_missing_place_id_preserves_summary(monkeypatch):
    page = Page("/maps/place/Cafe/")
    assert run(monkeypatch, page).address == "Summary address"
    assert not page.clicked

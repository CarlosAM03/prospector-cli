"""Controlled SPA navigation states without network or Chromium."""

import types

import pytest
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from engines.navigation.google_maps_navigation import GoogleMapsNavigation
from engines.selector import selector_engine


class Locator:
    def __init__(self, page, kind):
        self.page = page
        self.kind = kind

    def count(self):
        return int(self.page.tick >= self.page.appears.get(self.kind, 999))

    def is_visible(self):
        return self.count() > 0

    @property
    def first(self):
        return self

    def fill(self, value):
        self.page.filled = value

    def press(self, key):
        self.page.submitted = key == "Enter"
        if self.page.route_changes:
            self.page.url = "https://www.google.com/maps/search/cafes"


class Page:
    def __init__(self, appears=None, route_changes=True):
        self.tick = 0
        self.clock = 0.0
        self.appears = appears or {"input": 0, "feed": 0, "results": 0}
        self.route_changes = route_changes
        self.url = "https://www.google.com/maps"
        self.filled = None
        self.submitted = False

    def goto(self, url, wait_until):
        self.url = url

    def locator(self, selector):
        if selector.startswith("input["):
            kind = "input"
        elif selector == "div[role='feed']":
            kind = "feed"
        elif selector.startswith("a[href"):
            kind = "results"
        else:
            kind = "unknown"
        return Locator(self, kind)

    def wait_for_timeout(self, ms):
        self.clock += ms / 1000
        self.tick += 1

    def wait_for_url(self, pattern, timeout):
        if not self.url.startswith("https://www.google.com/maps/search/"):
            raise PlaywrightTimeoutError("route unchanged")


class Browser:
    def __init__(self, page):
        self.page = page

    def new_page(self):
        return self.page


def navigation(monkeypatch, appears=None, route_changes=True):
    page = Page(appears, route_changes)
    monkeypatch.setattr(selector_engine, "time", types.SimpleNamespace(monotonic=lambda: page.clock))
    return page, GoogleMapsNavigation(Browser(page), "google_maps")


def test_t_n01_home_and_result_ready_states(monkeypatch):
    page, nav = navigation(monkeypatch, {"input": 2, "feed": 4, "results": 6})
    assert nav.open() is page
    nav.search(page, "cafes Tijuana")
    assert page.filled == "cafes Tijuana" and page.submitted
    assert page.tick >= 6


def test_t_n02_missing_route_is_bounded_failure(monkeypatch):
    page, nav = navigation(monkeypatch, route_changes=False)
    nav.open()
    with pytest.raises(PlaywrightTimeoutError):
        nav.search(page, "cafes")


def test_t_n03_delayed_input_succeeds_but_missing_input_fails(monkeypatch):
    page, nav = navigation(monkeypatch, {"input": 3, "feed": 0, "results": 0})
    assert nav.open() is page
    page, nav = navigation(monkeypatch, {"input": 999, "feed": 0, "results": 0})
    with pytest.raises(PlaywrightTimeoutError):
        nav.open()


def test_t_n04_zero_links_are_not_verified_empty(monkeypatch):
    page, nav = navigation(monkeypatch, {"input": 0, "feed": 0, "results": 999})
    nav.open()
    with pytest.raises(PlaywrightTimeoutError):
        nav.search(page, "rare query")


def test_t_n05_url_before_feed_and_results_does_not_finish_early(monkeypatch):
    page, nav = navigation(monkeypatch, {"input": 0, "feed": 2, "results": 5})
    nav.open()
    nav.search(page, "cafes")
    assert page.tick >= 5


def test_t_n06_absent_feed_is_bounded_failure(monkeypatch):
    page, nav = navigation(monkeypatch, {"input": 0, "feed": 999, "results": 999})
    nav.open()
    with pytest.raises(PlaywrightTimeoutError):
        nav.search(page, "cafes")

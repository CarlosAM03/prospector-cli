"""Generic semantic wait remains independent of Google Maps parsing."""

import types

import pytest
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from engines.selector import selector_engine
from engines.selector.selector_engine import SelectorEngine


class Locator:
    def __init__(self, page, key):
        self.page, self.key = page, key

    def count(self):
        return int(self.page.tick >= self.page.appears.get(self.key, 999))

    def is_visible(self):
        return self.count() > 0

    @property
    def first(self):
        return self


class Page:
    def __init__(self):
        self.tick = 0
        self.clock = 0.0
        self.appears = {'input[name="q"]': 999, 'input[role="combobox"]': 3}

    def locator(self, selector):
        return Locator(self, selector)

    def wait_for_timeout(self, ms):
        self.tick += 1
        self.clock += ms / 1000


def test_t_s01_delayed_fallback_and_timeout(monkeypatch):
    page = Page()
    monkeypatch.setattr(selector_engine, "time", types.SimpleNamespace(monotonic=lambda: page.clock))
    engine = SelectorEngine(page, "google_maps")
    assert engine.wait_visible("search_box", timeout=1000).key == 'input[role="combobox"]'
    page.appears['input[role="combobox"]'] = 999
    with pytest.raises(PlaywrightTimeoutError):
        engine.wait_visible("search_box", timeout=100)

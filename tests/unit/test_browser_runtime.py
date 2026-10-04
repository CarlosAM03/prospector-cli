"""Per-search Playwright resource ownership without launching Chromium."""

import pytest

from engines import browser_runtime


class Page:
    def __init__(self):
        self.closes = 0

    def close(self):
        self.closes += 1


class Browser:
    def __init__(self):
        self.closes = 0
        self.pages = []

    def new_page(self):
        page = Page()
        self.pages.append(page)
        return page

    def close(self):
        self.closes += 1


class Playwright:
    def __init__(self, browser, launch_error=None):
        self.browser = browser
        self.launch_error = launch_error
        self.headless = None
        self.chromium = self

    def launch(self, headless):
        self.headless = headless
        if self.launch_error:
            raise self.launch_error
        return self.browser


class Context:
    def __init__(self, playwright):
        self.playwright = playwright
        self.exits = 0

    def __enter__(self):
        return self.playwright

    def __exit__(self, *args):
        self.exits += 1


def fixture(monkeypatch, launch_error=None):
    browser = Browser()
    playwright = Playwright(browser, launch_error)
    context = Context(playwright)
    monkeypatch.setattr(browser_runtime, "sync_playwright", lambda: context)
    return browser, playwright, context


def test_normal_ownership_and_headless_propagation(monkeypatch):
    browser, playwright, context = fixture(monkeypatch)
    with browser_runtime.BrowserRuntime(headless=True) as runtime:
        assert runtime.browser is browser
        first = runtime.new_page()
        second = runtime.new_page()
    assert playwright.headless is True
    assert (first.closes, second.closes, browser.closes, context.exits) == (1, 1, 1, 1)


def test_fatal_exception_is_preserved_and_resources_close_once(monkeypatch):
    browser, _, context = fixture(monkeypatch)
    with pytest.raises(RuntimeError, match="source failed"):
        with browser_runtime.BrowserRuntime() as runtime:
            page = runtime.new_page()
            raise RuntimeError("source failed")
    assert (page.closes, browser.closes, context.exits) == (1, 1, 1)


def test_launch_failure_releases_playwright_context(monkeypatch):
    browser, _, context = fixture(monkeypatch, ValueError("launch failed"))
    with pytest.raises(ValueError, match="launch failed"):
        with browser_runtime.BrowserRuntime():
            pass
    assert browser.closes == 0 and context.exits == 1


def test_launch_failure_is_preserved_when_context_cleanup_fails(monkeypatch):
    _, _, context = fixture(monkeypatch, ValueError("launch failed"))
    def failing_exit(*args):
        context.exits += 1
        raise OSError("cleanup failed")
    context.__exit__ = failing_exit
    with pytest.raises(ValueError, match="launch failed"):
        with browser_runtime.BrowserRuntime():
            pass
    assert context.exits == 1


def test_new_page_outside_runtime_is_rejected(monkeypatch):
    runtime = browser_runtime.BrowserRuntime()
    with pytest.raises(RuntimeError, match="not active"):
        runtime.new_page()


def test_cleanup_failure_does_not_mask_original_exception(monkeypatch):
    browser, _, context = fixture(monkeypatch)
    def bad_close():
        browser.closes += 1
        raise OSError("close failed")
    browser.close = bad_close
    with pytest.raises(RuntimeError, match="original"):
        with browser_runtime.BrowserRuntime():
            raise RuntimeError("original")
    assert browser.closes == 1 and context.exits == 1

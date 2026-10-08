"""Per-search Playwright resource ownership without launching Chromium."""

import pytest
import signal
import asyncio
import subprocess

from engines import browser_runtime
from engines.errors import ProspectorRuntimeError
from playwright.sync_api import Error as PlaywrightError
from cli_runtime import ExecutionCancelled, controlled_interrupt


def test_windows_playwright_driver_spawn_isolated_and_override_restored(monkeypatch):
    calls = []

    async def fake_spawn(*command, **options):
        calls.append((command, options))

    monkeypatch.setattr(browser_runtime.sys, "platform", "win32")
    monkeypatch.setattr(asyncio, "create_subprocess_exec", fake_spawn)
    with browser_runtime._isolate_playwright_driver_from_console_interrupt():
        asyncio.run(asyncio.create_subprocess_exec("node.exe", "driver.js", "run-driver"))
        asyncio.run(asyncio.create_subprocess_exec("other.exe"))
    assert asyncio.create_subprocess_exec is fake_spawn
    assert calls[0][1]["creationflags"] & subprocess.CREATE_NEW_PROCESS_GROUP
    assert "creationflags" not in calls[1][1]


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
        self.channel = None
        self.chromium = self

    def launch(self, *, headless, channel, timeout):
        self.headless = headless
        self.channel = channel
        assert timeout == 30000
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
    assert playwright.channel == "msedge"
    assert (first.closes, second.closes, browser.closes, context.exits) == (1, 1, 1, 1)


def test_visible_launch_uses_installed_edge_channel(monkeypatch):
    _, playwright, _ = fixture(monkeypatch)
    with browser_runtime.BrowserRuntime(headless=False):
        pass
    assert (playwright.channel, playwright.headless) == ("msedge", False)


def test_edge_launch_failure_is_actionable_and_logs_details(monkeypatch, caplog):
    _, playwright, context = fixture(monkeypatch, PlaywrightError("Executable does not exist"))
    with pytest.raises(ProspectorRuntimeError, match="Microsoft Edge Stable is required"):
        with browser_runtime.BrowserRuntime(headless=True):
            pass
    assert playwright.channel == "msedge"
    assert context.exits == 1
    assert "Executable does not exist" in caplog.text


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
    with pytest.raises(RuntimeError, match="original") as failure:
        with browser_runtime.BrowserRuntime():
            raise RuntimeError("original")
    assert browser.closes == 1 and context.exits == 1
    assert failure.value._prospector_cleanup_failed is True


def test_confirmed_ctrl_c_unwinds_through_browser_runtime(monkeypatch):
    browser, _, context = fixture(monkeypatch)
    with pytest.raises(ExecutionCancelled):
        with controlled_interrupt(lambda: True) as cancellation:
            with browser_runtime.BrowserRuntime() as runtime:
                page = runtime.new_page()
                signal.getsignal(signal.SIGINT)(signal.SIGINT, None)
                cancellation.raise_if_requested()
    assert (page.closes, browser.closes, context.exits) == (1, 1, 1)


def test_best_effort_process_exit_uses_existing_owner(monkeypatch):
    browser, _, context = fixture(monkeypatch)
    runtime = browser_runtime.BrowserRuntime()
    runtime.__enter__()
    page = runtime.new_page()
    runtime._best_effort_exit()
    runtime._best_effort_exit()
    assert (page.closes, browser.closes, context.exits) == (1, 1, 1)

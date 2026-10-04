"""Per-execution ownership of Playwright, Chromium and Maps pages."""

import sys
import logging

from playwright.sync_api import sync_playwright

logger = logging.getLogger(__name__)


class BrowserRuntime:
    """Own one browser execution; never pool resources across searches."""

    def __init__(self, *, headless: bool = False) -> None:
        self.headless = headless
        self.browser = None
        self._playwright_context = None
        self._pages = []

    def __enter__(self):
        self._playwright_context = sync_playwright()
        try:
            playwright = self._playwright_context.__enter__()
            self.browser = playwright.chromium.launch(headless=self.headless)
        except BaseException:
            original_error = sys.exc_info()
            try:
                self._playwright_context.__exit__(*original_error)
            except Exception as cleanup_error:
                logger.warning(
                    "Playwright startup cleanup failed after original error: %s",
                    cleanup_error,
                )
            self._playwright_context = None
            raise
        logger.debug("Browser runtime started: headless=%s", self.headless)
        return self

    def new_page(self):
        if self.browser is None:
            raise RuntimeError("BrowserRuntime is not active")
        page = self.browser.new_page()
        self._pages.append(page)
        return page

    def __exit__(self, exc_type, exc_value, traceback):
        close_error = None
        for page in reversed(self._pages):
            try:
                page.close()
            except Exception as error:
                close_error = close_error or error
        self._pages.clear()
        try:
            if self.browser is not None:
                self.browser.close()
        except Exception as error:
            close_error = close_error or error
        finally:
            self.browser = None
            context = self._playwright_context
            self._playwright_context = None
            if context is not None:
                try:
                    context.__exit__(exc_type, exc_value, traceback)
                except Exception as error:
                    close_error = close_error or error
        if exc_type is None and close_error is not None:
            logger.error("Browser runtime cleanup failed: %s", close_error)
            raise close_error
        if close_error is not None:
            logger.warning("Browser runtime cleanup failed after original error: %s", close_error)
        else:
            logger.debug("Browser runtime closed")
        return False

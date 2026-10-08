"""Per-execution ownership of Playwright, installed Edge and Maps pages."""

import sys
import logging
import atexit
import asyncio
import subprocess
from contextlib import contextmanager

from playwright.sync_api import sync_playwright
from playwright.sync_api import Error as PlaywrightError

from engines.errors import ProspectorRuntimeError

logger = logging.getLogger(__name__)


@contextmanager
def _isolate_playwright_driver_from_console_interrupt():
    """Keep Windows Ctrl+C in the CLI from killing Playwright's Node driver.

    Playwright starts its driver during sync_playwright().__enter__(). Scope the
    spawn override to that synchronous startup; no worker or browser lifecycle
    ownership is moved outside BrowserRuntime.
    """
    if sys.platform != "win32":
        yield
        return
    original_spawn = asyncio.create_subprocess_exec

    async def spawn(*command, **options):
        if command and command[-1] == "run-driver":
            options["creationflags"] = (
                options.get("creationflags", 0) | subprocess.CREATE_NEW_PROCESS_GROUP
            )
        return await original_spawn(*command, **options)

    asyncio.create_subprocess_exec = spawn
    try:
        yield
    finally:
        asyncio.create_subprocess_exec = original_spawn


class BrowserRuntime:
    """Own one browser execution; never pool resources across searches."""

    def __init__(self, *, headless: bool = False) -> None:
        self.headless = headless
        self.browser = None
        self._playwright_context = None
        self._pages = []
        self._exit_callback = self._best_effort_exit

    def __enter__(self):
        self._playwright_context = sync_playwright()
        try:
            with _isolate_playwright_driver_from_console_interrupt():
                playwright = self._playwright_context.__enter__()
            try:
                self.browser = playwright.chromium.launch(
                    channel="msedge", headless=self.headless, timeout=30000,
                )
            except (PlaywrightError, OSError) as error:
                logger.exception("Microsoft Edge Stable launch failed")
                raise ProspectorRuntimeError(
                    "Microsoft Edge Stable is required. Prospector could not launch "
                    "Microsoft Edge on this system. Install or restore Edge and try "
                    "again; on a managed device, contact your administrator."
                ) from error
        except BaseException:
            original_error = sys.exc_info()
            try:
                self._playwright_context.__exit__(*original_error)
            except Exception as cleanup_error:
                if original_error[1] is not None:
                    original_error[1]._prospector_cleanup_failed = True
                logger.warning(
                    "Playwright startup cleanup failed after original error: %s",
                    type(cleanup_error).__name__,
                )
            self._playwright_context = None
            raise
        logger.debug("Microsoft Edge runtime started: headless=%s", self.headless)
        atexit.register(self._exit_callback)
        return self

    def _best_effort_exit(self):
        """Try owned cleanup at ordinary interpreter exit; forced OS exit may bypass it."""
        if self._playwright_context is None:
            return
        try:
            self.__exit__(None, None, None)
        except Exception:
            logger.exception("Best-effort browser cleanup at process exit failed")

    def new_page(self):
        if self.browser is None:
            raise RuntimeError("BrowserRuntime is not active")
        page = self.browser.new_page()
        self._pages.append(page)
        return page

    def __exit__(self, exc_type, exc_value, traceback):
        atexit.unregister(self._exit_callback)
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
            logger.error("Browser runtime cleanup failed: %s", type(close_error).__name__)
            raise close_error
        if close_error is not None:
            if exc_value is not None:
                exc_value._prospector_cleanup_failed = True
            logger.warning("Browser runtime cleanup failed after original error: %s", type(close_error).__name__)
        else:
            logger.debug("Browser runtime closed")
        return False

"""
Lazy Charge Engine.

Modern web applications frequently render their DOM
asynchronously.

Elements may exist only after network requests, lazy loading,
virtual scrolling or client-side rendering.

The Lazy Charge Engine centralizes every synchronization
operation required before selector resolution.

Responsibilities
----------------

- Wait for semantic selectors.
- Detect optional content.
- Synchronize scraper execution with DOM rendering.
- Keep waiting logic independent from scraping logic.

The Lazy Charge Engine never parses page content.

It only coordinates DOM readiness.
"""

from playwright.sync_api import (
    Locator,
    TimeoutError,
)

from .selector_engine import SelectorEngine


class LazyChargeEngine:
    """
    DOM synchronization engine.

    Parameters
    ----------
    page:
        Playwright page instance.

    profile:
        Registered selector profile.
    """

    def __init__(
        self,
        page,
        profile: str,
    ) -> None:

        self._selector = SelectorEngine(
            page=page,
            profile=profile,
        )

    def wait(
        self,
        name: str,
        timeout: int = 10000,
    ) -> Locator:
        """
        Wait until a semantic selector becomes visible.

        Parameters
        ----------
        name:
            Semantic selector name.

        timeout:
            Maximum waiting time in milliseconds.

        Returns
        -------
        Locator

        Raises
        ------
        TimeoutError
            If the selector never appears.
        """

        locator = self._selector.locator(
            name
        )

        locator.wait_for(
            state="visible",
            timeout=timeout,
        )

        return locator

    def optional(
        self,
        name: str,
        timeout: int = 1000,
    ) -> Locator | None:
        """
        Wait for an optional selector.

        Returns
        -------
        Locator | None
        """

        try:

            return self.wait(
                name=name,
                timeout=timeout,
            )

        except (
            LookupError,
            TimeoutError,
        ):

            return None

    def loaded(
        self,
        name: str,
        timeout: int = 10000,
    ) -> bool:
        """
        Determine whether a semantic selector
        becomes available before timeout.
        """

        return (
            self.optional(
                name=name,
                timeout=timeout,
            )
            is not None
        )

    def wait_hidden(
        self,
        name: str,
        timeout: int = 10000,
    ) -> None:
        """
        Wait until a semantic selector disappears.
        """

        locator = self._selector.locator(
            name
        )

        locator.wait_for(
            state="hidden",
            timeout=timeout,
        )

    def wait_detached(
        self,
        name: str,
        timeout: int = 10000,
    ) -> None:
        """
        Wait until a semantic selector is detached
        from the DOM.
        """

        locator = self._selector.locator(
            name
        )

        locator.wait_for(
            state="detached",
            timeout=timeout,
        )
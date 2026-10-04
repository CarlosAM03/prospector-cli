"""
Selector Engine.

The Selector Engine provides a semantic interface over selector
profiles.

Instead of exposing raw CSS selectors throughout the scraper, the
engine resolves semantic selector names using the Selector Registry
and delegates selector election to the Elector Engine.

Responsibilities
----------------

- Resolve semantic selector names.
- Retrieve selector candidates from a profile.
- Delegate selector election.
- Expose convenience Playwright helpers.

The Selector Engine never contains scraper logic.

It only coordinates selector resolution.
"""

import time

from playwright.sync_api import Locator, TimeoutError as PlaywrightTimeoutError

from .elector_engine import ElectorEngine
from .registry import SelectorRegistry


class SelectorEngine:
    """
    Semantic selector resolver.

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

        self._registry = SelectorRegistry()

        self._elector = ElectorEngine(page)

        self._profile = profile

    def selectors(
        self,
        name: str,
    ) -> list[str]:
        """
        Return every selector candidate associated with
        a semantic selector name.
        """

        return self._registry.selectors(
            self._profile,
            name,
        )

    def locator(
        self,
        name: str,
    ) -> Locator:
        """
        Return the elected locator associated with a
        semantic selector.
        """

        selectors = self.selectors(
            name
        )

        return self._elector.elect(
            selectors
        )

    def wait_visible(self, name: str, timeout: int = 10000) -> Locator:
        """Wait for any semantic candidate, even if mounted after the call."""
        candidates = self.selectors(name)
        deadline = time.monotonic() + timeout / 1000
        while True:
            for candidate in candidates:
                try:
                    locator = self._elector.page.locator(candidate)
                    if locator.count() and locator.first.is_visible():
                        return locator
                except Exception:
                    continue
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise PlaywrightTimeoutError(
                    f"No visible selector for {name!r} within {timeout} ms"
                )
            self._elector.page.wait_for_timeout(
                min(100, max(1, int(remaining * 1000)))
            )

    def optional(
        self,
        name: str,
    ) -> Locator | None:
        """
        Return a locator when available.

        Returns
        -------
        Locator | None
        """

        selectors = self.selectors(
            name
        )

        return self._elector.optional(
            selectors
        )

    def exists(
        self,
        name: str,
    ) -> bool:
        """
        Determine whether a semantic selector exists.
        """

        selectors = self.selectors(
            name
        )

        return self._elector.exists(
            selectors
        )

    def first(
        self,
        name: str,
    ) -> Locator:
        """
        Return the first matching element.
        """

        return self.locator(
            name
        ).first

    def nth(
        self,
        name: str,
        index: int,
    ) -> Locator:
        """
        Return the nth matching element.
        """

        return self.locator(
            name
        ).nth(index)

    def count(
        self,
        name: str,
    ) -> int:
        """
        Return the number of matching elements.
        """

        return self.locator(
            name
        ).count()

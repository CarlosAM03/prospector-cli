"""
Selector Engine.

The Selector Engine provides a semantic interface over Playwright
DOM queries.

Instead of querying raw CSS selectors throughout the scraper, the
engine resolves semantic selector names using a registered profile.

Responsibilities
----------------

- Resolve selector aliases.
- Try selector fallbacks.
- Return Playwright locators.
- Keep scraper code independent from DOM structure.

The engine never contains scraper logic.

It only performs DOM access.
"""

from playwright.sync_api import Locator

from .registry import SelectorRegistry


class SelectorEngine:
    """
    Generic selector engine.

    Parameters
    ----------
    page:
        Playwright page.

    profile:
        Registered selector profile name.
    """

    def __init__(
        self,
        page,
        profile: str,
    ) -> None:

        self.page = page

        self.registry = SelectorRegistry()

        self.profile = profile

    def locator(
        self,
        name: str,
    ) -> Locator:
        """
        Return the first locator matching a semantic selector.

        Every selector registered under the semantic name is
        attempted in order.

        Returns
        -------
        Playwright Locator

        Raises
        ------
        LookupError

            If no selector matches.
        """

        selectors = self.registry.selectors(
            self.profile,
            name,
        )

        for selector in selectors:

            locator = self.page.locator(
                selector
            )

            try:

                if locator.count() > 0:
                    return locator

            except Exception:
                continue

        raise LookupError(
            f"No selector found for '{name}'."
        )

    def optional(
        self,
        name: str,
    ) -> Locator | None:
        """
        Return a locator if available.

        Returns None when no selector matches.
        """

        try:

            return self.locator(
                name
            )

        except LookupError:

            return None

    def exists(
        self,
        name: str,
    ) -> bool:
        """
        Check whether a semantic selector exists.
        """

        return (
            self.optional(name)
            is not None
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
        Return the amount of matching elements.
        """

        return self.locator(
            name
        ).count()
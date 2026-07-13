"""
Elector Engine.

The Elector Engine is responsible for selecting the first usable
selector from a selector profile.

Selector profiles may define multiple selectors for the same
semantic field. This engine evaluates them in order and returns
the first selector capable of locating elements.

Responsibilities
----------------

- Evaluate selector candidates.
- Apply fallback strategy.
- Keep selector selection independent from scraper logic.

The Elector Engine never parses page content.

It only decides which selector should be used.
"""

from playwright.sync_api import Locator


class ElectorEngine:
    """
    Selector election strategy.

    Parameters
    ----------
    page:
        Playwright page instance.
    """

    def __init__(
        self,
        page,
    ) -> None:

        self.page = page

    def elect(
        self,
        selectors: list[str],
    ) -> Locator:
        """
        Return the first selector producing at least one element.

        Parameters
        ----------
        selectors:
            Ordered selector candidates.

        Returns
        -------
        Locator

        Raises
        ------
        LookupError
            If every selector fails.
        """

        for selector in selectors:

            try:

                locator = self.page.locator(
                    selector
                )

                if locator.count() > 0:
                    return locator

            except Exception:

                #
                # Ignore invalid selectors and
                # continue evaluating fallbacks.
                #

                continue

        raise LookupError(
            "No selector candidate matched."
        )

    def optional(
        self,
        selectors: list[str],
    ) -> Locator | None:
        """
        Return a locator if one exists.

        Returns
        -------
        Locator | None
        """

        try:

            return self.elect(
                selectors
            )

        except LookupError:

            return None

    def exists(
        self,
        selectors: list[str],
    ) -> bool:
        """
        Determine whether at least one selector matches.
        """

        return (
            self.optional(selectors)
            is not None
        )
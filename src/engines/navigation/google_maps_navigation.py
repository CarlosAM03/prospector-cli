"""
Google Maps Navigation.

This module contains the Google Maps implementation of the
Navigation Engine.

Responsibilities
----------------

- Create browser pages.
- Open Google Maps.
- Execute searches through the Google Maps UI.

Navigation synchronization remains intentionally minimal during
Commit 2. Advanced synchronization will be introduced in the next
commit.
"""

from playwright.sync_api import (
    Browser,
    Page,
)

from engines.selector import SelectorEngine


class GoogleMapsNavigation:
    """
    Google Maps navigation implementation.

    Parameters
    ----------
    browser:
        Playwright browser instance.
    """

    MAPS_URL = "https://www.google.com/maps"

    def __init__(
        self,
        browser: Browser,
    ) -> None:

        self.browser = browser

    def open(
        self,
    ) -> Page:
        """
        Open Google Maps.

        Returns
        -------
        Page
            Playwright page positioned at the Google Maps home.
        """

        page = self.browser.new_page()

        page.goto(
            self.MAPS_URL,
            wait_until="domcontentloaded",
        )

        return page

    def search(
        self,
        page: Page,
        query: str,
    ) -> None:
        """
        Execute a search using the Google Maps interface.

        Parameters
        ----------
        page:
            Active Playwright page.

        query:
            Search text.
        """

        selector = SelectorEngine(page)

        search_box = selector.locator(
            "search_box"
        )

        search_box.wait_for(
            state="visible",
            timeout=10000,
        )

        search_box.fill(query)

        search_box.press("Enter")
"""
Google Maps Navigation.

This module contains the Google Maps implementation of the
Navigation Engine.

Responsibilities
----------------

- Create browser pages.
- Open Google Maps.
- Return a ready Playwright page.

The navigation implementation intentionally does not perform:

- Search execution.
- Selector resolution.
- Synchronization.
- Scraping.
- Data extraction.

Its only responsibility during v0.7.0 Commit 1 is opening the
Google Maps application.
"""

from playwright.sync_api import (
    Browser,
    Page,
)


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
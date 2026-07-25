"""
Google Maps Navigation.

This module contains the Google Maps implementation of the
Navigation Engine.

Responsibilities
----------------

- Create browser pages.
- Open Google Maps.
- Wait until the Google Maps home is ready.
- Execute searches through the Google Maps UI.
- Wait until the search results page is ready.

This module never performs scraping or data extraction.
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

    profile:
        Selector profile associated with Google Maps.
    """

    MAPS_URL = "https://www.google.com/maps"

    def __init__(
        self,
        browser: Browser,
        profile: str,
    ) -> None:

        self.browser = browser
        self.profile = profile

    def open(
        self,
    ) -> Page:
        """
        Open Google Maps and wait until the home page is ready.

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

        #
        # Google Maps is a SPA.
        #
        # DOMContentLoaded only guarantees that the initial HTML
        # has been received. Give the application a brief moment
        # to mount before resolving semantic selectors.
        #

        selector = SelectorEngine(
            page=page,
            profile=self.profile,
        )

        search_box = selector.locator(
            "search_box",
        ).wait_for(
            state="visible",
            timeout=10000,
        )

        return page

    def search(
        self,
        page: Page,
        query: str,
    ) -> None:
        """
        Execute a Google Maps search.

        Parameters
        ----------
        page:
            Active Playwright page.

        query:
            Search text.
        """

        selector = SelectorEngine(
            page=page,
            profile=self.profile,
        )

        search_box = selector.locator(
            "search_box",
        )
        #
        # Google Maps may recreate the input element
        # after the initial application mount.
        #
        # Resolve the locator immediately before typing.
        #
        search_box.wait_for(
            state="visible",
            timeout=10000,
        )

        search_box.fill(query)

        search_box.press("Enter")
        
        page.wait_for_url(
            "**/maps/search/**",
            timeout=15000,
        )

        #
        # Navigation contract:
        #
        # Return only after Google Maps has transitioned
        # from the Home view to the Search Results view.
        #

        selector.locator(
            "feed",
        ).wait_for(
            state="visible",
            timeout=10000,
        )
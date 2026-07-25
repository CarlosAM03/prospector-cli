"""
Navigation Engine.

This module exposes the public navigation interface used by
scrapers.

Scrapers should never instantiate source-specific navigation
implementations directly.

Instead, they interact exclusively with NavigationEngine, which
delegates navigation responsibilities to the configured
implementation.

Current implementation
----------------------

- GoogleMapsNavigation

Future implementations may include:

- LinkedInNavigation
- FacebookNavigation
- YellowPagesNavigation
"""

from playwright.sync_api import (
    Browser,
    Page,
)

from models.search_query import Source

from .google_maps_navigation import GoogleMapsNavigation


class NavigationEngine:
    """
    Public navigation interface.

    Parameters
    ----------
    browser:
        Playwright browser instance.
    """

    def __init__(
            self,
            browser: Browser,
            source: Source,
        ) -> None:

            if source == Source.GOOGLE_MAPS:

                self._navigation = GoogleMapsNavigation(
                    browser=browser,
                    profile="google_maps",
                )

            else:

                raise ValueError(
                    f"Unsupported navigation source: {source}"
                )

    def open(
        self,
    ) -> Page:
        """
        Open the configured source application.

        Returns
        -------
        Page
            Ready Playwright page.
        """

        return self._navigation.open()

    def search(
        self,
        page: Page,
        query: str,
    ) -> None:
        """
        Execute a search using the configured navigation
        implementation.

        Parameters
        ----------
        page:
            Active Playwright page.

        query:
            Search text.
        """

        self._navigation.search(
            page,
            query,
        )
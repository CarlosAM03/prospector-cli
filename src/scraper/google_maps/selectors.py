"""
Google Maps selector factory.

This module provides the Selector Engine configured for the
Google Maps selector profile.

Scraper modules should never import selector profiles directly.

Instead, they should request a configured SelectorEngine
through this factory.
"""

from engines.selector.selector_engine import SelectorEngine


PROFILE_NAME = "google_maps"


def create_selector_engine(
    page,
) -> SelectorEngine:
    """
    Create a Selector Engine configured for Google Maps.

    Parameters
    ----------
    page:
        Playwright page instance.

    Returns
    -------
    SelectorEngine
        Configured selector engine.
    """

    return SelectorEngine(
        page=page,
        profile=PROFILE_NAME,
    )
"""
Navigation Engine package.

This package provides navigation infrastructure used by source
scrapers.

The Navigation Engine is responsible for opening web applications
and preparing browser pages before any interaction or extraction
takes place.

Navigation implementations are source-specific while exposing a
consistent public interface through the Navigation Engine.

Current implementations
-----------------------

- Google Maps

Future versions may include:

- LinkedIn
- Facebook
- Yelp
- Yellow Pages
"""

from .navigation_engine import NavigationEngine
from .google_maps_navigation import GoogleMapsNavigation

__all__ = [
    "NavigationEngine",
    "GoogleMapsNavigation",
]
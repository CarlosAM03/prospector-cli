"""
Website Engine package.

This package provides website inspection infrastructure.

The Website Engine is responsible for retrieving and processing
external website information independently from source scrapers.
"""

from .crawler import WebsiteCrawler


__all__ = [
    "WebsiteCrawler",
]
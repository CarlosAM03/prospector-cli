"""
Website Engine package.

This package provides website inspection infrastructure.

The Website Engine retrieves, parses and structures external
website information independently from source scrapers.
"""


from .crawler import WebsiteCrawler
from .parser import WebsiteParser
from .metadata import WebsiteMetadataBuilder
from .website_engine import WebsiteEngine


__all__ = [
    "WebsiteCrawler",
    "WebsiteParser",
    "WebsiteMetadataBuilder",
    "WebsiteEngine",
]
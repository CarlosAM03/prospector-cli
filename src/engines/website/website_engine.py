"""
Website Engine.

The Website Engine orchestrates website inspection workflow.

It coordinates every internal component required to transform
a website URL into structured website information.

Pipeline
--------

Website URL

    ↓

Crawler

    ↓

WebsiteDocument

    ↓

Parser

    ↓

Parsed Website Data

    ↓

WebsiteExtractor

    ↓

WebsiteMetadata


Responsibilities
----------------

- Coordinate website inspection pipeline.
- Manage internal website components.
- Return structured metadata.

The Website Engine does not:

- Extract website metadata.
- Detect languages.
- Extract emails.
- Perform HTML parsing.
- Perform HTTP requests.
"""

from playwright.sync_api import Browser

from engines.website.crawler import WebsiteCrawler
from engines.website.parser import WebsiteParser
from engines.website.extractor import WebsiteExtractor

from models.website_metadata import WebsiteMetadata


class WebsiteEngine:
    """
    Main website inspection engine.

    Parameters
    ----------
    browser:
        Playwright browser instance.
    """

    def __init__(
        self,
        browser: Browser,
    ) -> None:

        self._crawler = WebsiteCrawler(
            browser
        )

        self._parser = WebsiteParser()

        self._extractor = WebsiteExtractor()

    def inspect(
        self,
        url: str,
    ) -> WebsiteMetadata:
        """
        Inspect a website and return structured metadata.

        Parameters
        ----------
        url:
            Website URL.

        Returns
        -------
        WebsiteMetadata
        """

        document = self._crawler.crawl(
            url
        )

        parsed = self._parser.parse(
            document
        )

        metadata = self._extractor.extract(
            parsed
        )

        return metadata
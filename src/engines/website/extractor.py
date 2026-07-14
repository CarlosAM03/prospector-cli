"""
Website Extractor.

The Website Extractor orchestrates every website extraction
component.

It receives parsed website data and coordinates specialized
extractors responsible for producing structured website
information.

Pipeline
--------

Parsed Website Data

        │

        ├── Metadata Builder

        ├── Language Detector

        ├── Email Extractor

        └── Future Extractors

                │

                ▼

        WebsiteMetadata


Responsibilities
----------------

- Coordinate website extraction.
- Invoke specialized extractors.
- Merge extracted information.
- Return WebsiteMetadata.

The Website Extractor does not:

- Crawl websites.
- Parse HTML.
- Perform HTTP requests.
"""

from engines.website.email import EmailExtractor
from engines.website.lenguaje import LanguageDetector
from engines.website.metadata import WebsiteMetadataBuilder

from models.website_metadata import WebsiteMetadata

class WebsiteExtractor:
    """
    Website extraction pipeline.
    """


    def __init__(
        self,
    ) -> None:

        self._metadata = WebsiteMetadataBuilder()

        self._language = LanguageDetector()

        self._emails = EmailExtractor()

    def extract(
        self,
        parsed: dict,
    ) -> WebsiteMetadata:
        """
        Execute the website extraction pipeline.

        Parameters
        ----------
        parsed:
            Parsed website information.

        Returns
        -------
        WebsiteMetadata
        """


        #
        # Base metadata
        #

        metadata = self._metadata.build(
            parsed
        )

        #
        # Language detection
        #

        language = self._language.detect(
            parsed
        )

        if language:

            metadata.language = language
        #
        # Email extraction
        #
        # Emails are discovered from parsed website
        # information and stored as part of the website
        # metadata model.
        #

        metadata.emails = self._emails.extract(
            parsed
        )

        #
        # Future enrichment points:
        #
        # - Social networks
        # - WhatsApp
        # - Contact forms
        # - Technologies
        # - Company size
        #

        return metadata
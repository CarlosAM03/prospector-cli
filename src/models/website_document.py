from dataclasses import dataclass


@dataclass
class WebsiteDocument:
    """
    Raw website document produced by the Website Crawler.

    This model represents the downloaded webpage before any
    parsing or metadata extraction occurs.

    Responsibilities
    ----------------
    
    - Store the final resolved URL.
    - Store raw HTML content.
    - Store HTTP response information.

    This model does not perform:
    
    - HTML parsing.
    - Metadata extraction.
    - Email extraction.
    - Business enrichment.
    """

    url: str

    html: str

    status_code: int

    content_type: str | None = None
from dataclasses import dataclass


@dataclass
class WebsiteDocument:
    """
    Raw website document produced by the Website Crawler.

    This model represents the downloaded webpage before any
    parsing or metadata extraction occurs.
    """

    url: str

    html: str

    status_code: int

    language: str | None = None
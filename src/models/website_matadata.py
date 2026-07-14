from dataclasses import dataclass


@dataclass
class WebsiteMetadata:
    """
    Parsed metadata extracted from a website document.
    """

    title: str | None = None

    description: str | None = None

    language: str | None = None

    has_contact_page: bool = False

    has_about_page: bool = False
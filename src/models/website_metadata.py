from dataclasses import dataclass, field


@dataclass
class WebsiteMetadata:
    """
    Parsed metadata extracted from a website document.

    This model represents structured information obtained
    after processing a WebsiteDocument.

    Responsibilities
    ----------------

    - Store extracted website metadata.
    - Store detected website characteristics.
    - Store discovered contact information.
    - Provide enrichment data for Business objects.

    This model does not perform:

    - HTML parsing.
    - HTTP requests.
    - Crawling.
    """


    title: str | None = None

    description: str | None = None

    language: str | None = None

    domain: str | None = None

    final_url: str | None = None


    #
    # Contact information
    #

    emails: list[str] = field(
        default_factory=list
    )


    #
    # Website characteristics
    #

    has_contact_page: bool = False

    has_about_page: bool = False


    #
    # HTTP information
    #

    status_code: int | None = None
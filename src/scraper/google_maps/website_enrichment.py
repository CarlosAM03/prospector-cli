from playwright.sync_api import Browser

from engines.website.website_engine import WebsiteEngine

from models.business import Business


def enrich_websites(
    browser: Browser,
    businesses: list[Business],
) -> list[Business]:
    """
    Execute website enrichment for every business.

    Responsibilities
    ----------------

    - Inspect every available website.
    - Merge extracted metadata.
    - Preserve Google Maps information.

    Businesses without a website are skipped.

    Returns
    -------
    list[Business]
        Enriched businesses.
    """

    website_engine = WebsiteEngine(
        browser
    )

    for business in businesses:

        if not business.website:
            continue

        metadata = website_engine.inspect(
            business.website
        )

        _merge_metadata(
            business,
            metadata,
        )

    return businesses


def _merge_metadata(
    business: Business,
    metadata,
) -> None:
    """
    Merge Website Engine metadata into a Business.

    Existing Google Maps information is never overwritten.
    """

    business.website_title = (
        metadata.title
    )

    business.website_description = (
        metadata.description
    )

    business.language = (
        metadata.language
    )

    business.has_contact_page = (
        metadata.has_contact_page
    )

    business.has_about_page = (
        metadata.has_about_page
    )

    business.website_status = (
        metadata.status_code
    )
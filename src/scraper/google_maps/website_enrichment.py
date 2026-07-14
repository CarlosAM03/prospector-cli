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
    - Extract website metadata.
    - Extract language information.
    - Extract email information.
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

        try:

            metadata = website_engine.inspect(
                business.website
            )


            _merge_metadata(
                business,
                metadata,
            )


        except Exception:

            #
            # Website failures must not
            # invalidate the scraping pipeline.
            #

            continue

    return businesses

def _merge_metadata(
    business: Business,
    metadata,
) -> None:
    """
    Merge Website Engine metadata into Business.

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

    #
    # Email enrichment.
    #
    # WebsiteMetadata stores extracted emails.
    # Business keeps a primary email field.
    #

    if metadata.emails:

        business.email = metadata.emails[0]
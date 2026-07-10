from playwright.sync_api import TimeoutError

from models.business import Business

from .selectors import (
    ADDRESS_TEXT,
    PHONE_TEXT,
    WEBSITE_LINK,
    ADDRESS_BUTTON,
)


def enrich_business(
    page,
    link,
    business: Business
) -> Business:

    try:

        link.click(
            force=True,
            no_wait_after=True
        )

        page.wait_for_selector(
            ADDRESS_BUTTON,
            timeout=3000
        )

    except TimeoutError:

        return business

    #
    # Dirección
    #

    try:

        address = page.locator(
            ADDRESS_TEXT
        ).first.inner_text()

        if address:

            business.address = address.strip()

    except Exception:
        pass

    #
    # Teléfono
    #

    try:

        phone = page.locator(
            PHONE_TEXT
        ).first.inner_text()

        if phone:

            business.phone = phone.strip()

    except Exception:
        pass

    #
    # Sitio web
    #

    try:

        website = page.locator(
            WEBSITE_LINK
        ).first.get_attribute(
            "href"
        )

        if website:

            business.website = website.strip()

    except Exception:
        pass

    return business
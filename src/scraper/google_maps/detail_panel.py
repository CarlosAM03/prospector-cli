import re

from playwright.sync_api import TimeoutError

from models.business import Business

from .selectors import create_selector_engine


def extract_place_id(
    href: str,
) -> str | None:
    """
    Extract the Google Maps Place ID from a business href.
    """

    match = re.search(
        r"1s([^!]+)",
        href,
    )

    if match:
        return match.group(1)

    return None


def enrich_business(
    page,
    href: str,
    business: Business,
) -> Business:
    """
    Enrich a Business using the Google Maps detail panel.

    Responsibilities
    ----------------

    - Open the detail panel.
    - Wait for the selected business.
    - Read address.
    - Read phone.
    - Read website.
    - Merge information into the Business model.

    This function intentionally does NOT inspect websites.

    Website enrichment belongs to the Website Engine and is
    executed during Phase 3 of the Google Maps pipeline.
    """

    place_id = extract_place_id(
        href
    )

    if place_id is None:
        return business

    selector = create_selector_engine(
        page
    )

    #
    # Open detail panel.
    #

    page.evaluate(
        """
        href => {

            const link = document.querySelector(
                `a[href="${href}"]`
            );

            if (link) {
                link.click();
            }

        }
        """,
        href,
    )

    #
    # Wait until Google Maps updates
    # the displayed business.
    #

    try:

        page.wait_for_function(
            """
            placeId => {

                return window.location.href.includes(
                    placeId
                );

            }
            """,
            arg=place_id,
            timeout=3000,
        )

    except TimeoutError:

        return business

    #
    # Resolve semantic selectors.
    #

    address_selector = (
        selector.selectors(
            "address"
        )[0]
    )

    phone_selector = (
        selector.selectors(
            "phone"
        )[0]
    )

    website_selector = (
        selector.selectors(
            "website"
        )[0]
    )

    #
    # Read the complete detail panel
    # using a single JavaScript evaluation.
    #

    data = page.evaluate(
        """
        selectors => ({

            address:
                document.querySelector(
                    selectors.address
                )?.innerText ?? null,

            phone:
                document.querySelector(
                    selectors.phone
                )?.innerText ?? null,

            website:
                document.querySelector(
                    selectors.website
                )?.href ?? null

        })
        """,
        {
            "address": address_selector,
            "phone": phone_selector,
            "website": website_selector,
        },
    )

    #
    # Merge Google Maps information.
    #

    if data["address"]:
        business.address = data["address"]

    if data["phone"]:
        business.phone = data["phone"]

    if data["website"]:
        business.website = data["website"]

    return business
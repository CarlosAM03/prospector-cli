import re

from playwright.sync_api import TimeoutError

from models.business import Business

from .selectors import create_selector_engine


def extract_place_id(
    href: str,
) -> str | None:

    match = re.search(
        r"1s([^!]+)",
        href,
    )

    if match:
        return match.group(1)

    return None


def enrich_business(
    page,
    href,
    business: Business,
) -> Business:

    place_id = extract_place_id(
        href
    )

    if place_id is None:
        return business

    selector = create_selector_engine(
        page
    )

    #
    # Click mediante JavaScript
    #

    page.evaluate(
        """
        href => {

            const link = document.querySelector(
                `a[href="${href}"]`
            );

            if(link){
                link.click();
            }

        }
        """,
        href,
    )

    #
    # Esperar cambio de panel
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
    # Resolver selectores semánticos
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
    # Leer panel completo
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
    # Merge sin degradar información existente
    #

    if data["address"]:
        business.address = data["address"]

    if data["phone"]:
        business.phone = data["phone"]

    if data["website"]:
        business.website = data["website"]

    return business
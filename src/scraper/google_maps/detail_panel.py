import re

from playwright.sync_api import TimeoutError

from models.business import Business


def extract_place_id(href: str) -> str | None:

    match = re.search(
        r"1s([^!]+)",
        href
    )

    if match:
        return match.group(1)

    return None


def enrich_business(
    page,
    href,
    business: Business
) -> Business:

    place_id = extract_place_id(href)

    if place_id is None:
        return business

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
        href
    )

    #
    # Esperar únicamente el cambio del panel
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
            timeout=3000
        )

    except TimeoutError:

        return business

    #
    # Leer todo el panel en una sola llamada JS
    #

    data = page.evaluate(
        """
        () => ({

            address:
                document.querySelector(
                    "button[data-item-id='address'] .Io6YTe"
                )?.innerText ?? null,

            phone:
                document.querySelector(
                    "a[data-item-id^='phone:'] .Io6YTe"
                )?.innerText ?? null,

            website:
                document.querySelector(
                    "a[data-item-id='authority']"
                )?.href ?? null

        })
        """
    )

    #
    # Merge de información
    # Nunca degradar datos existentes.
    #

    if data["address"]:
        business.address = data["address"]

    if data["phone"]:
        business.phone = data["phone"]

    if data["website"]:
        business.website = data["website"]

    return business
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

    #
    # Título actual
    #

    place_id = extract_place_id(href)

    if place_id is None:

        return business

    #
    # Click usando JavaScript
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
    # Leer todo el panel en una sola llamada
    #

    data = page.evaluate(
        """
        () => {

            return {

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

            };

        }
        """
    )

    business.address = data["address"]
    business.phone = data["phone"]
    business.website = data["website"]

    return business
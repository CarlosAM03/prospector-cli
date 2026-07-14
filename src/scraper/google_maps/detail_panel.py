import re

from playwright.sync_api import TimeoutError

from models.business import Business

from utils.parser import is_phone

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
    # Synchronize with Google Maps state.
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
    # Resolve selectors.
    #

    address_selector = selector.selectors(
        "address"
    )[0]


    phone_selector = selector.selectors(
        "phone"
    )[0]


    website_selector = selector.selectors(
        "website"
    )[0]



    #
    # Extract detail data.
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
    # Merge Google Maps data.
    #

    if data["address"]:

        business.address = data["address"]



    if data["phone"]:

        business.phone = data["phone"]



    if data["website"]:

        business.website = data["website"]



    return business




def parse_business_summary(
    info_blocks,
):

    category = None
    address = None
    phone = None



    for block_index in range(
        info_blocks.count()
    ):

        text = info_blocks.nth(
            block_index
        ).inner_text()



        parts = [

            item.strip()

            for item in text.split("·")

            if item.strip()

        ]



        for item in parts:

            if is_phone(item):

                phone = item



            elif item and category is None:

                if block_index > 0:

                    category = item



        if len(parts) >= 2:

            possible_address = parts[-1]


            if (

                not is_phone(
                    possible_address
                )

                and possible_address != category

            ):

                address = possible_address



    return category, address, phone
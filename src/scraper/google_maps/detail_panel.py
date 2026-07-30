import re

from playwright.sync_api import TimeoutError

from models.business import Business

from engines.selector.lazycharge import LazyChargeEngine

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
    identity: dict | None = None,
) -> Business:

    print(
        f"\n>>> Enriqueciendo: {business.name}"
    )

    place_id = extract_place_id(
        href
    )

    if place_id is None:

        print(
            "  [EXIT] place_id no encontrado."
        )

        return business

    selector = create_selector_engine(
        page
    )

    lazycharge = LazyChargeEngine(
        page=page,
        profile="google_maps",
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

    print(
        "  ✓ Click realizado."
    )

    #
    # Synchronize detail panel.
    #

    try:

        panel = lazycharge.wait_detail_panel()

        print(
            "  ✓ Detail panel visible."
        )

        #lazycharge.wait_detail_content()

        print(
            "  ✓ Detail content renderizado."
        )

    except TimeoutError:

        print(
            "  [EXIT] Timeout esperando detail panel."
        )

        return business

    #
    # Validate navigation identity.
    #

    print(
        "  → Validando place_id..."
    )

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

        print(
            "  ✓ place_id validado."
        )

    except TimeoutError:

        print(
            "  [EXIT] place_id no coincide."
        )

        return business

    #
    # Validate business identity.
    #

    if identity:

        print(
            "  → Validando nombre..."
        )

        name_selector = selector.selectors(
            "business_name"
        )[0]

        try:

            detail_name = (
                panel.locator(
                    name_selector
                )
                .last
                .inner_text()
                .strip()
            )

        except Exception:

            detail_name = None

        print(
            "     Esperado:",
            identity["name"],
        )

        print(
            "     Encontrado:",
            detail_name,
        )

        if not detail_name:

            print(
                "  [EXIT] Nombre vacío."
            )

            return business

        if detail_name.strip() != identity["name"].strip():

            print(
                "  [EXIT] Nombre diferente."
            )

            return business

        print(
            "  ✓ Nombre validado."
        )

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

    print(
        "  → Extrayendo datos..."
    )

    #
    # Extract detail data.
    #

    try:

        address = (
            panel.locator(
                address_selector
            )
            .last
            .inner_text()
        )

    except Exception:

        address = None


    try:

        phone = (
            panel.locator(
                phone_selector
            )
            .last
            .inner_text()
        )

    except Exception:

        phone = None


    try:

        website = (
            panel.locator(
                website_selector
            )
            .last
            .get_attribute(
                "href"
            )
        )

    except Exception:

        website = None


    data = {
        "address": address,
        "phone": phone,
        "website": website,
    }

    print(
        "     Address:",
        data["address"],
    )

    print(
        "     Phone:",
        data["phone"],
    )

    print(
        "     Website:",
        data["website"],
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

    print(
        "  ✓ Enriquecimiento completado."
    )

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
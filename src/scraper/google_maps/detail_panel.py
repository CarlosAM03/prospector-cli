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
def read_text(
    panel,
    selector,
):

    try:

        return (
            panel.locator(
                selector
            )
            .last
            .inner_text(
                timeout=1000,
            )
            .strip()
        )

    except Exception:

        return None


def read_href(
    panel,
    selector,
):

    try:

        return (
            panel.locator(
                selector
            )
            .last
            .get_attribute(
                "href",
                timeout=1000,
            )
        )

    except Exception:

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
    name_selector = selector.selectors(
        "business_name"
    )[0]

    lazycharge = LazyChargeEngine(
        page=page,
        profile="google_maps",
    )

    #
    # Open detail panel.
    #
    previous_name = read_text(
        page,
        name_selector,
    )
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
    if previous_name:

        try:

            page.wait_for_function(
                """
                previous => {

                    const title = document.querySelector("h1");

                    return (
                        title &&
                        title.innerText.trim() !== previous
                    );

                }
                """,
                arg=previous_name,
                timeout=2000,
            )

        except TimeoutError:

            pass
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
        if identity:

            try:

                page.wait_for_function(
                    """
                    expected => {

                        const title = document.querySelector("h1");

                        return (
                            title &&
                            title.innerText.trim() === expected
                        );

                    }
                    """,
                    arg=identity["name"],
                    timeout=2000,
                )

            except TimeoutError:

                pass
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

        detail_name = read_text(
            panel,
            name_selector,
        )

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

        if detail_name != identity["name"].strip():

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

    address = read_text(
        panel,
        address_selector,
    )

    phone = read_text(
        panel,
        phone_selector,
    )

    website = read_href(
        panel,
        website_selector,
    )

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
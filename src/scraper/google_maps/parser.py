from utils.parser import is_phone
from engines._timing import remaining_ms


def category_repeats_address(category: str | None, address: str | None) -> bool:
    """Detect a summary category that is exactly the address's first segment.

    The summary DOM can provide an address without a category. An available
    address from the same Business supplies a narrow cross-field check.
    """
    if not category or not address:
        return False
    fragment = category.strip()
    return any(char.isdigit() for char in fragment) and address.strip().casefold().startswith(
        fragment.casefold() + ","
    )


def parse_business_summary(info_blocks, *, deadline=None):

    category = None
    address = None
    phone = None

    for block_index in range(info_blocks.count()):

        block = info_blocks.nth(block_index)
        text = (
            block.inner_text(timeout=remaining_ms(deadline, 1000))
            if deadline is not None else block.inner_text()
        )

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
                not is_phone(possible_address)
                and possible_address != category
            ):
                address = possible_address

    return category, address, phone

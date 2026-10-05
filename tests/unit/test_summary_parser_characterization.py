from scraper.google_maps.parser import (
    category_repeats_address, parse_business_summary,
)


class Blocks:
    def __init__(self, values):
        self.values = values

    def count(self):
        return len(self.values)

    def nth(self, index):
        return Block(self.values[index])


class Block:
    def __init__(self, value):
        self.value = value

    def inner_text(self):
        return self.value


def test_characterization_summary_parser_current_encoding_and_phone_behavior():
    result = parse_business_summary(
        Blocks(["Restaurante Â· 555-123-4567", "Centro Â· 123 Main"])
    )

    # Characterization only: this records the current separator behavior.
    assert result[2] == "555-123-4567"


def test_observed_summary_address_fragment_is_not_a_category_after_detail():
    category, _, _ = parse_business_summary(
        Blocks(["4.5 estrellas", "C. Pacifico 9030"])
    )
    assert category == "C. Pacifico 9030"
    assert category_repeats_address(
        category,
        "C. Pacifico 9030, Parque Industrial Pacifico II, 22643 Tijuana, B.C.",
    )
    assert category_repeats_address(
        "C. Pacifico 9030",
        "C. Pacifico 9030, Parque Industrial Pacifico II, 22643 Tijuana, B.C.",
    )
    assert category_repeats_address(
        "Avenida Universidad 102",
        "Avenida Universidad 102, Otayjardin II, 22424 Tijuana, B.C.",
    )
    assert category_repeats_address(
        "C. 5 Sur 155", "C. 5 Sur 155, Cd Industrial, 22444 Tijuana, B.C."
    )


def test_category_reconciliation_requires_address_evidence():
    assert not category_repeats_address("Fábrica", "C. 5 Sur 155, Tijuana")
    assert not category_repeats_address("Fábrica", "Fábrica, Tijuana")
    assert not category_repeats_address("C. 5 Sur 155", None)
    assert not category_repeats_address("C. 5 Sur 155", "C. 5 Sur 1550, Tijuana")

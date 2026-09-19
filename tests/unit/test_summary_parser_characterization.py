from scraper.google_maps.parser import parse_business_summary


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

import pytest

from engines.normalization import rules


@pytest.mark.parametrize("source,expected", [
    ("  Clínica   Médica del Río  ", "CLÍNICA MÉDICA DEL RÍO"),
    ("A&B, S.A.", "A&B, S.A."),
    ("   ", "   "),
])
def test_name_rule(source, expected):
    assert rules.normalize_name(source) == expected
    assert rules.normalize_name(expected) == expected


@pytest.mark.parametrize("source,expected", [
    (" Hospital   privado ", "HOSPITAL PRIVADO"),
    ("C. 5 Sur 155", "C. 5 SUR 155"),  # presentation only, no extraction repair
    (None, None),
])
def test_category_rule(source, expected):
    assert rules.normalize_category(source) == expected
    assert rules.normalize_category(expected) == expected


def test_address_preserves_structure_and_case():
    value = "  Av. Diego Rivera 2312, Tijuana, B.C.  "
    expected = "Av. Diego Rivera 2312, Tijuana, B.C."
    assert rules.normalize_address(value) == expected
    assert rules.normalize_address(expected) == expected
    assert rules.normalize_address(None) is None


@pytest.mark.parametrize("source,expected,unverifiable", [
    ("6641234567", "664 123 4567", False),
    ("(664) 123-4567", "664 123 4567", False),
    ("664.123.4567", "664 123 4567", False),
    ("+1 (619) 301-9068", "+1 619 301 9068", False),
    ("664 123 4567 ext. 25", "664 123 4567 ext. 25", False),
    ("+52 664 123 4567", "+52 664 123 4567", False),
    ("664 123 4567 ext. texto", "664 123 4567 ext. texto", False),
    ("6641234", "6641234", True),
    ("664-ABC-4567", "664-ABC-4567", True),
    ("unknown", "unknown", True),
    ("664...123...4567", "664...123...4567", True),
    (None, None, False),
])
def test_phone_rule_is_conservative(source, expected, unverifiable):
    assert rules.normalize_phone(source) == expected
    assert rules.normalize_phone(expected) == expected
    assert rules.phone_is_unverifiable(source) is unverifiable


def test_website_keeps_sensitive_components():
    value = " https://Example.com/Products/ItemA?id=7#Part "
    expected = "https://Example.com/Products/ItemA?id=7#Part"
    assert rules.normalize_website(value) == expected
    assert rules.normalize_website(expected) == expected
    assert rules.normalize_website(None) is None


@pytest.mark.parametrize("source,expected", [
    ("  INFO@EXAMPLE.COM ", "info@example.com"),
    ("974-9586impex@mcna.com.mx", "974-9586impex@mcna.com.mx"),
    (None, None),
])
def test_email_keeps_complete_value(source, expected):
    assert rules.normalize_email(source) == expected
    assert rules.normalize_email(expected) == expected


@pytest.mark.parametrize("source,expected", [
    (" es-MX ", "ES-MX"),
    ("en-US", "EN-US"),
    (None, None),
])
def test_language_keeps_subtags(source, expected):
    assert rules.normalize_language(source) == expected
    assert rules.normalize_language(expected) == expected


def test_metadata_values_are_outside_the_rule_catalog():
    assert not any(name.startswith("normalize_website_title") for name in dir(rules))
    assert not any(name.startswith("normalize_website_status") for name in dir(rules))

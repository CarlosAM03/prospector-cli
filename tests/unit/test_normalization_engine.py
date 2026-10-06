from copy import deepcopy

import pytest

from engines.issue_collector import IssueCollector
from engines.normalization import NormalizationEngine, rules
from engines.normalization.normalization_engine import FieldUnavailable
from models.business import Business
from models.normalized_business import NormalizedBusiness


def test_complete_business_maps_without_mutating_original():
    original = Business(
        name="  Clínica  Río ", category=" Hospital privado ",
        address="  Av. Diego Rivera 2312, Tijuana  ",
        phone="(664) 123-4567",
        website=" https://Example.test/Path?X=1 ",
        email=" INFO@EXAMPLE.TEST ", language=" es-MX ",
        website_title="Brand Case", website_description="Text, with punctuation.",
        has_contact_page=False, has_about_page=None, website_status=200,
    )
    before = deepcopy(original)
    collector = IssueCollector()
    actual = NormalizationEngine().normalize_business(
        original, candidate="business[0]", issue_collector=collector,
    )
    assert isinstance(actual, NormalizedBusiness)
    assert actual is not original
    assert original == before
    assert (actual.name, actual.category, actual.phone, actual.email, actual.language) == (
        "CLÍNICA RÍO", "HOSPITAL PRIVADO", "664 123 4567", "info@example.test", "ES-MX",
    )
    assert actual.address == "Av. Diego Rivera 2312, Tijuana"
    assert actual.website == "https://Example.test/Path?X=1"
    assert (actual.website_title, actual.website_description, actual.has_contact_page,
            actual.has_about_page, actual.website_status) == (
        "Brand Case", "Text, with punctuation.", False, None, 200,
    )
    assert collector.items == []
    actual.name = "CHANGED"
    assert original == before


def test_collection_keeps_order_cardinality_and_repeated_names():
    originals = [Business(" cafe ", phone="6641234567"), Business(" cafe ", phone="12345")]
    collector = IssueCollector()
    actual = NormalizationEngine().normalize_businesses(
        originals, issue_collector=collector,
    )
    assert [item.name for item in actual] == ["CAFE", "CAFE"]
    assert [item.phone for item in actual] == ["664 123 4567", "12345"]
    assert len(actual) == len(originals) == 2
    assert originals[0].name == originals[1].name == " cafe "
    assert [(item.stage, item.code, item.candidate) for item in collector.items] == [
        ("normalization", "field_unverifiable", "business[1].phone"),
    ]


def test_optional_absence_and_policy_preservation_do_not_emit_issues():
    original = Business("Cafe", phone="664 123 4567 ext. 25", website_title="Original")
    collector = IssueCollector()
    actual = NormalizationEngine().normalize_business(
        original, issue_collector=collector,
    )
    assert actual.phone == original.phone
    assert actual.website_title == original.website_title
    assert actual.category is None
    assert collector.items == []


def test_controlled_field_failure_preserves_field_and_continues(monkeypatch):
    def unavailable(_):
        raise FieldUnavailable()

    monkeypatch.setattr(rules, "normalize_category", unavailable)
    collector = IssueCollector()
    original = Business(" cafe ", category=" Bistro ", email=" INFO@EXAMPLE.TEST ")
    actual = NormalizationEngine().normalize_business(
        original, candidate="private raw value", issue_collector=collector,
    )
    assert (actual.name, actual.category, actual.email) == (
        "CAFE", " Bistro ", "info@example.test",
    )
    assert original.category == " Bistro "
    assert len(collector.items) == 1
    issue = collector.items[0]
    assert (issue.stage, issue.code, issue.candidate) == (
        "normalization", "field_unavailable", "business[?].category",
    )
    assert "private raw value" not in repr(issue)
    assert "Bistro" not in repr(issue)


def test_unexpected_programming_error_is_not_hidden(monkeypatch):
    def broken(_):
        raise RuntimeError("program defect")

    monkeypatch.setattr(rules, "normalize_email", broken)
    with pytest.raises(RuntimeError, match="program defect"):
        NormalizationEngine().normalize_business(Business("Cafe", email="a@test.com"))


def test_normalization_is_deterministic_and_idempotent():
    source = Business(" cafe ", category=" Bistro ", phone="(664) 123-4567")
    normalizer = NormalizationEngine()
    first = normalizer.normalize_business(source)
    second = normalizer.normalize_business(source)
    third = normalizer.normalize_business(Business(**vars(first)))
    assert first == second == third
    assert source.name == " cafe "


def test_future_mutable_field_does_not_share_state():
    original = Business("Cafe", website_description={"parts": ["text"]})
    normalized = NormalizationEngine().normalize_business(original)
    normalized.website_description["parts"].append("changed")
    assert original.website_description == {"parts": ["text"]}

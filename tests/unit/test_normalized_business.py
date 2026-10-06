from dataclasses import fields

import pytest

from models.business import Business
from models.normalized_business import NormalizedBusiness
from models.search_query import SearchQuery, Source
from models.search_result import SearchResult


FIELD_NAMES = (
    "name", "category", "address", "phone", "website", "email", "language",
    "website_title", "website_description", "has_contact_page",
    "has_about_page", "website_status",
)


def test_normalized_business_is_separate_with_matching_fields_and_defaults():
    assert NormalizedBusiness is not Business
    assert tuple(field.name for field in fields(NormalizedBusiness)) == FIELD_NAMES
    normalized = NormalizedBusiness("CAFE")
    assert normalized.name == "CAFE"
    assert all(getattr(normalized, name) is None for name in FIELD_NAMES[1:])


def test_search_result_holds_independent_corresponding_views():
    query = SearchQuery(Source.GOOGLE_MAPS, "cafe", "Tijuana")
    original = Business("Cafe")
    normalized = NormalizedBusiness("CAFE")
    result = SearchResult(
        query, [normalized], 1.25, [], original_businesses=[original],
    )
    assert result.total_found == 1
    assert result.businesses[0] is not result.original_businesses[0]
    normalized.name = "CHANGED"
    assert original.name == "Cafe"
    assert result.execution_time == 1.25


def test_transitional_result_rejects_mixed_or_unpaired_views():
    query = SearchQuery(Source.GOOGLE_MAPS, "cafe", "Tijuana")
    with pytest.raises(TypeError, match="NormalizedBusiness"):
        SearchResult(query, [Business("A"), NormalizedBusiness("B")])
    with pytest.raises(TypeError, match="NormalizedBusiness"):
        SearchResult(query, [Business("A")], original_businesses=[Business("A")])
    with pytest.raises(ValueError, match="counts must match"):
        SearchResult(query, [NormalizedBusiness("A")], original_businesses=[Business("A"), Business("B")])


def test_default_original_collections_are_independent():
    query = SearchQuery(Source.GOOGLE_MAPS, "cafe", "Tijuana")
    first, second = SearchResult(query), SearchResult(query)
    first.original_businesses.append(Business("A"))
    assert second.original_businesses == []

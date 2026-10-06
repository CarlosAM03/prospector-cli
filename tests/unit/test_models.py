from dataclasses import FrozenInstanceError

import pytest

from models.business import Business
from models.normalized_business import NormalizedBusiness
from models.search_query import SearchQuery, Source
from models.search_result import SearchResult
from models.search_issue import SearchIssue
from models.website_document import WebsiteDocument
from models.website_metadata import WebsiteMetadata


def test_search_result_total_found_matches_business_count():
    query = SearchQuery(Source.GOOGLE_MAPS, "cafes", "Tijuana")
    result = SearchResult(
        query=query, businesses=[NormalizedBusiness("A"), NormalizedBusiness("B")],
        original_businesses=[Business("A"), Business("B")],
    )

    assert result.total_found == 2


def test_search_result_preserves_query_and_business_order():
    query = SearchQuery(Source.GOOGLE_MAPS, "cafes", "Tijuana")
    businesses = [NormalizedBusiness("A"), NormalizedBusiness("B")]
    result = SearchResult(
        query=query, businesses=businesses,
        original_businesses=[Business("A"), Business("B")],
    )

    assert result.query is query
    assert result.businesses == businesses


def test_models_expose_observed_optional_defaults():
    business = Business("A")
    document = WebsiteDocument(url="https://example.test", html="", status_code=200)
    metadata = WebsiteMetadata()

    assert business.website is None
    assert business.email is None
    assert document.content_type is None
    assert metadata.emails == []
    assert metadata.has_contact_page is False
    assert metadata.has_about_page is False


def test_default_lists_are_independent_between_instances():
    first_result = SearchResult(SearchQuery(Source.GOOGLE_MAPS, "a", "b"))
    second_result = SearchResult(SearchQuery(Source.GOOGLE_MAPS, "a", "b"))
    first_metadata = WebsiteMetadata()
    second_metadata = WebsiteMetadata()

    first_result.businesses.append(NormalizedBusiness("A"))
    first_result.issues.append(SearchIssue("feed", "partial_results", "Safe."))
    first_metadata.emails.append("a@example.test")

    assert second_result.businesses == []
    assert second_result.issues == []
    assert second_metadata.emails == []


def test_legacy_positional_search_result_and_public_issue_order():
    query = SearchQuery(Source.GOOGLE_MAPS, "cafes", "Tijuana")
    result = SearchResult(
        query, [NormalizedBusiness("A")], 1.25,
        original_businesses=[Business("A")],
    )
    assert result.issues == [] and result.total_found == 1
    first = SearchIssue("detail", "identity_unverifiable", "Safe detail message")
    second = SearchIssue("website", "inspection_unavailable", "Safe website message")
    result.issues.extend([first, second])
    assert result.issues == [first, second]
    assert result.total_found == 1
    with pytest.raises(FrozenInstanceError):
        first.code = "different"

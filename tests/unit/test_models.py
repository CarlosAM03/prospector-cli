from models.business import Business
from models.search_query import SearchQuery, Source
from models.search_result import SearchResult
from models.website_document import WebsiteDocument
from models.website_metadata import WebsiteMetadata


def test_search_result_total_found_matches_business_count():
    query = SearchQuery(Source.GOOGLE_MAPS, "cafes", "Tijuana")
    result = SearchResult(query=query, businesses=[Business("A"), Business("B")])

    assert result.total_found == 2


def test_search_result_preserves_query_and_business_order():
    query = SearchQuery(Source.GOOGLE_MAPS, "cafes", "Tijuana")
    businesses = [Business("A"), Business("B")]
    result = SearchResult(query=query, businesses=businesses)

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

    first_result.businesses.append(Business("A"))
    first_metadata.emails.append("a@example.test")

    assert second_result.businesses == []
    assert second_metadata.emails == []

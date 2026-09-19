import os

import pytest

from models.search_query import SearchQuery, Source
from models.search_result import SearchResult
from scraper.google_maps.scraper import search_businesses


@pytest.mark.e2e
def test_google_maps_smoke_preserves_high_level_result_invariants():
    if os.environ.get("PROSPECTOR_RUN_E2E") != "1":
        pytest.skip("Set PROSPECTOR_RUN_E2E=1 to run the live external smoke test")

    query = SearchQuery(Source.GOOGLE_MAPS, "cafes", "Tijuana")
    result = search_businesses(query, limit=3)

    assert isinstance(result, SearchResult)
    assert result.query == query
    assert result.total_found <= 3
    assert len(result.businesses) <= 3
    assert result.execution_time >= 0
    assert all(business.name.strip() for business in result.businesses)

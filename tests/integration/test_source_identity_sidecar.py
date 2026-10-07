"""P92 private global transport and structural failure contracts."""

import pytest

from engines.global_pipeline import execute_global_search_with_identities
from models.business import Business
from models.search_query import SearchQuery, Source
from models.source_identity import SourceIdentityEvidence
from scraper.google_maps.scraper import _SourceResult


def query():
    return SearchQuery(Source.GOOGLE_MAPS, "cafes", "Tijuana")


def test_private_global_result_keeps_source_sidecar_and_originals():
    original = Business("  Cafe  ")
    evidence = SourceIdentityEvidence.unverified("test_unknown")
    execution = execute_global_search_with_identities(
        lambda: _SourceResult(query(), [original], identities=[evidence]),
    )
    assert execution.identities == (evidence,)
    assert execution.result.businesses[0].name == "CAFE"
    assert execution.result.original_businesses[0] is original
    assert execution.result.total_found == 1


def test_source_rejects_missing_or_misaligned_sidecar():
    with pytest.raises(ValueError, match="sidecar"):
        _SourceResult(query(), [Business("Cafe")])
    with pytest.raises(ValueError, match="sidecar"):
        _SourceResult(query(), [Business("Cafe")], identities=[
            SourceIdentityEvidence.unverified(), SourceIdentityEvidence.unverified(),
        ])

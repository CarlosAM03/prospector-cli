"""P94 exact cross-query selection with no commercial-field merging."""

from engines.batch import select_batch_exports
from models.batch import (
    BatchQuery, BatchQueryResult, BatchSearchResult, ObservationDisposition,
    ObservationProvenance, ObservationRef, QueryFailure, QueryStatus,
)
from models.business import Business
from models.normalized_business import NormalizedBusiness
from models.search_query import SearchQuery, Source
from models.search_result import SearchResult
from models.source_identity import VerifiedSourceIdentity


def place(value, source=Source.GOOGLE_MAPS, kind="google_place_id"):
    return VerifiedSourceIdentity(source, kind, value)


def entry(index, identities, *, status=QueryStatus.SUCCESS, names=None):
    query = SearchQuery(Source.GOOGLE_MAPS, f"query {index}", "Tijuana")
    request = BatchQuery(query, 50)
    if status is QueryStatus.FAILED:
        return BatchQueryResult(request, status, error=QueryFailure("navigation", "Safe."))
    names = names or [f"Business {index}-{item}" for item in range(len(identities))]
    result = SearchResult(
        query, [NormalizedBusiness(name=name.upper()) for name in names],
        original_businesses=[Business(name) for name in names],
    )
    observations = tuple(
        ObservationProvenance(
            ObservationRef(index, position), identity,
            ObservationDisposition.EXPORTED if identity is not None
            else ObservationDisposition.IDENTITY_UNVERIFIED_EXPORTED,
        ) for position, identity in enumerate(identities)
    )
    return BatchQueryResult(
        request, status, result=result, export_indices=list(range(len(identities))),
        unverified_identity_indices=[i for i, identity in enumerate(identities) if identity is None],
        observations=observations,
    )


def test_abc_first_verified_occurrence_wins_across_queries_only():
    original = BatchSearchResult([
        entry(0, [place("1"), place("2"), place("3")]),
        entry(1, [place("2"), place("4"), place("5")]),
        entry(2, [place("1"), place("5"), place("6")]),
    ])
    selected = select_batch_exports(original)
    assert [item.export_indices for item in selected.entries] == [[0, 1, 2], [1, 2], [2]]
    assert selected.total_observations == 9
    assert selected.total_exportable == 6
    assert selected.duplicates_suppressed == 3
    assert [(d.duplicate, d.winner) for item in selected.entries for d in item.suppressed] == [
        (ObservationRef(1, 0), ObservationRef(0, 1)),
        (ObservationRef(2, 0), ObservationRef(0, 0)),
        (ObservationRef(2, 1), ObservationRef(1, 2)),
    ]
    assert original.entries[1].export_indices == [0, 1, 2]
    assert selected.entries[1].result is original.entries[1].result
    assert selected.entries[1].result.total_found == 3


def test_duplicate_within_first_query_remains_exportable_and_winner_is_first():
    selected = select_batch_exports(BatchSearchResult([
        entry(0, [place("same"), place("same")]),
        entry(1, [place("same")]),
    ]))
    assert selected.entries[0].export_indices == [0, 1]
    assert selected.entries[1].suppressed[0].winner == ObservationRef(0, 0)


def test_failed_does_not_contribute_but_partial_does():
    selected = select_batch_exports(BatchSearchResult([
        entry(0, [], status=QueryStatus.FAILED),
        entry(1, [place("A")], status=QueryStatus.PARTIAL),
        entry(2, [place("A")]),
    ]))
    assert selected.entries[0].result is None
    assert selected.entries[1].export_indices == [0]
    assert selected.entries[2].suppressed[0].winner == ObservationRef(1, 0)


def test_unknown_identity_and_distinct_namespace_remain_exportable():
    selected = select_batch_exports(BatchSearchResult([
        entry(0, [None, place("A")]),
        entry(1, [None, place("A", kind="other_namespace"), place("B")]),
    ]))
    assert selected.entries[1].export_indices == [0, 1, 2]
    assert selected.entries[1].unverified_identity_indices == [0]
    assert selected.total_unverified == 2


def test_homonyms_branches_and_complementary_fields_are_not_merged():
    first = entry(0, [place("branch-one"), place("branch-two")], names=["Starbucks", "Starbucks"])
    second = entry(1, [place("branch-one"), place("branch-three")], names=["Better Name", "Starbucks"])
    selected = select_batch_exports(BatchSearchResult([first, second]))
    assert selected.entries[1].export_indices == [1]
    assert selected.entries[1].suppressed[0].winner == ObservationRef(0, 0)
    assert first.result.original_businesses[0].name == "Starbucks"
    assert second.result.original_businesses[0].name == "Better Name"
    assert selected.entries[0].result is first.result
    assert selected.entries[1].result is second.result


def test_two_identical_queries_remain_distinct_entries():
    a = entry(0, [place("x")])
    b = entry(1, [place("x")])
    b.request.query.keyword = a.request.query.keyword
    selected = select_batch_exports(BatchSearchResult([a, b]))
    assert len(selected.entries) == 2
    assert selected.entries[1].export_indices == []


def test_repeated_selection_is_deterministic_and_idempotent():
    batch = BatchSearchResult([entry(0, [place("a"), None]), entry(1, [place("a"), None])])
    once = select_batch_exports(batch)
    twice = select_batch_exports(once)
    assert once == twice
    assert once.entries[1].observations[0].disposition is ObservationDisposition.SUPPRESSED_DUPLICATE
    assert once.entries[1].observations[0].winner == ObservationRef(0, 0)


def test_misaligned_provenance_is_not_silently_deduped():
    bad = entry(0, [place("x")])
    bad.observations = ()
    try:
        select_batch_exports(BatchSearchResult([bad]))
    except ValueError as error:
        assert "aligned" in str(error)
    else:
        raise AssertionError("misaligned provenance must fail")

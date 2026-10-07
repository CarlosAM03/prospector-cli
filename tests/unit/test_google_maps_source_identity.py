"""P92 conservative, evidence-derived Google Maps Place ID admission."""

import pytest

from models.search_query import Source
from models.source_identity import VerificationState
from scraper.google_maps.source_identity import verified_place_identity


RIO_FEATURE = "0x80d94840107994c1:0x95f9d1c6296e50c3"
RIO_PLACE = "ChIJwZR5EEBI2YARw1BuKcbR-ZU"
OTAY_FEATURE = "0x80d94795c4dfdb89:0xec6b16defc35d695"
OTAY_PLACE = "ChIJidvfxJVH2YARldY1_N4Wa-w"


def href(feature=RIO_FEATURE, place_id=RIO_PLACE):
    return (
        "https://www.google.com/maps/place/Starbucks/data="
        f"!4m7!3m6!1s{feature}!8m2!3d32.5!4d-117!19s{place_id}"
    )


def selected(feature=RIO_FEATURE):
    return (
        "https://www.google.com/maps/place/Starbucks/data="
        f"!3m6!1s{feature}!8m2!3d32.5!4d-117"
    )


def test_same_branch_and_distinct_branch_have_exact_namespaced_ids():
    first = verified_place_identity(href(), selected())
    again = verified_place_identity(href(), selected())
    other = verified_place_identity(href(OTAY_FEATURE, OTAY_PLACE), selected(OTAY_FEATURE))
    assert first == again
    assert first.verification_state is VerificationState.VERIFIED
    assert first.verified.source is Source.GOOGLE_MAPS
    assert first.verified.kind == "google_place_id"
    assert first.verified.value == RIO_PLACE
    assert other.verified != first.verified


@pytest.mark.parametrize("candidate,target", [
    (href(), None),
    (href(), selected(OTAY_FEATURE)),
    (href().replace("!19s", "!20s"), selected()),
    (href().replace(RIO_PLACE, "unknown"), selected()),
    (href() + "!19s" + OTAY_PLACE, selected()),
    (href().replace("www.google.com", "example.test"), selected()),
    (href() + f"!3m6!1s{RIO_FEATURE}!8m2", selected()),
    (href(), selected().replace("www.google.com", "example.test")),
    (href(), selected().replace("/maps/place/", "/maps/search/")),
])
def test_missing_ambiguous_unknown_or_wrong_panel_never_verifies(candidate, target):
    evidence = verified_place_identity(candidate, target)
    assert evidence.verified is None
    assert evidence.verification_state is VerificationState.UNVERIFIED

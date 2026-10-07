"""Conservative Place ID evidence from one confirmed Maps candidate/panel."""

import re
from urllib.parse import unquote, urlsplit

from models.search_query import Source
from models.source_identity import SourceIdentityEvidence, VerificationState, VerifiedSourceIdentity


_FEATURE = re.compile(r"!3m6!1s(0x[0-9a-f]+:0x[0-9a-f]+)!8m2")
_PLACE_ID = re.compile(r"(?:^|!)19s(ChIJ[A-Za-z0-9_-]{23})(?=!|$)")


def _maps_place_path(url: str) -> str | None:
    try:
        parsed = urlsplit(url)
    except ValueError:
        return None
    if parsed.scheme != "https" or parsed.hostname != "www.google.com":
        return None
    path = unquote(parsed.path)
    return path if path.startswith("/maps/place/") else None


def verified_place_identity(
    candidate_href: str, selected_url: str | None,
) -> SourceIdentityEvidence:
    """Admit only the live-observed Place ID namespace with a confirmed target.

    `selected_url` is supplied only after the detail-panel identity gate passed.
    A raw href or navigation token alone can never produce VERIFIED.
    """
    candidate = _maps_place_path(candidate_href)
    selected = _maps_place_path(selected_url) if selected_url else None
    if candidate is None or selected is None:
        return SourceIdentityEvidence.unverified("candidate_or_panel_unverified")
    features = _FEATURE.findall(candidate)
    place_ids = _PLACE_ID.findall(candidate)
    selected_features = _FEATURE.findall(selected)
    if (len(features) != 1 or len(place_ids) != 1
            or len(selected_features) != 1 or selected_features[0] != features[0]):
        return SourceIdentityEvidence.unverified("source_identity_ambiguous")
    return SourceIdentityEvidence(
        VerifiedSourceIdentity(Source.GOOGLE_MAPS, "google_place_id", place_ids[0]),
        VerificationState.VERIFIED, "confirmed_candidate_panel",
    )

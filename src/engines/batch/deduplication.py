"""Select cross-query exports by exact, verified source identity only."""

from dataclasses import replace

from models.batch import (
    BatchQueryResult, BatchSearchResult, DuplicateReference,
    ObservationDisposition, ObservationProvenance, ObservationRef, QueryStatus,
)
from models.source_identity import VerifiedSourceIdentity


def select_batch_exports(batch: BatchSearchResult) -> BatchSearchResult:
    """Return a new batch view; never alter its individual SearchResults."""
    seen_previous: dict[VerifiedSourceIdentity, ObservationRef] = {}
    selected: list[BatchQueryResult] = []
    for query_index, entry in enumerate(batch.entries):
        if entry.status is QueryStatus.FAILED:
            selected.append(replace(entry))
            continue
        if entry.result is None or len(entry.observations) != entry.result.total_found:
            raise ValueError("batch provenance is not aligned with the result")
        seen_current: dict[VerifiedSourceIdentity, ObservationRef] = {}
        export_indices: list[int] = []
        suppressed: list[DuplicateReference] = []
        unverified_indices: list[int] = []
        provenance: list[ObservationProvenance] = []
        for business_index, observed in enumerate(entry.observations):
            reference = ObservationRef(query_index, business_index)
            if observed.observation != reference:
                raise ValueError("batch provenance references a different observation")
            identity = observed.identity
            if identity is None:
                export_indices.append(business_index)
                unverified_indices.append(business_index)
                disposition = ObservationDisposition.IDENTITY_UNVERIFIED_EXPORTED
                winner = None
            elif identity in seen_previous:
                winner = seen_previous[identity]
                suppressed.append(DuplicateReference(reference, winner, identity))
                disposition = ObservationDisposition.SUPPRESSED_DUPLICATE
            else:
                export_indices.append(business_index)
                seen_current.setdefault(identity, reference)
                disposition = ObservationDisposition.EXPORTED
                winner = None
            provenance.append(ObservationProvenance(reference, identity, disposition, winner))
        selected.append(replace(
            entry, export_indices=export_indices, suppressed=suppressed,
            unverified_identity_indices=unverified_indices, observations=tuple(provenance),
        ))
        for identity, reference in seen_current.items():
            seen_previous.setdefault(identity, reference)
    result = BatchSearchResult(selected, batch.execution_time)
    if result.total_observations != result.total_exportable + result.duplicates_suppressed:
        raise ValueError("batch observation partition is inconsistent")
    return result

"""Public contracts for a bounded, sequential multi-query operation."""

from dataclasses import dataclass, field
from enum import Enum

from models.search_query import SearchQuery
from models.search_result import SearchResult
from models.source_identity import VerifiedSourceIdentity


@dataclass(frozen=True)
class BatchQuery:
    """A shallow-frozen request; the Engine snapshots its mutable query."""

    query: SearchQuery
    limit: int


class QueryStatus(str, Enum):
    SUCCESS = "success"
    SUCCESS_WITH_ISSUES = "success_with_issues"
    PARTIAL = "partial"
    FAILED = "failed"


class ObservationDisposition(str, Enum):
    EXPORTED = "exported"
    SUPPRESSED_DUPLICATE = "suppressed_duplicate"
    IDENTITY_UNVERIFIED_EXPORTED = "identity_unverified_exported"


@dataclass(frozen=True)
class ObservationRef:
    query_index: int
    business_index: int

    def __post_init__(self) -> None:
        if (type(self.query_index) is not int or self.query_index < 0
                or type(self.business_index) is not int or self.business_index < 0):
            raise ValueError("observation indices must be nonnegative integers")


@dataclass(frozen=True)
class DuplicateReference:
    duplicate: ObservationRef
    winner: ObservationRef
    identity: VerifiedSourceIdentity

    def __post_init__(self) -> None:
        if self.winner.query_index >= self.duplicate.query_index:
            raise ValueError("duplicate winner must belong to an earlier query")


@dataclass(frozen=True)
class QueryFailure:
    category: str
    message: str
    exception_type: str | None = None


@dataclass(frozen=True)
class ObservationProvenance:
    observation: ObservationRef
    identity: VerifiedSourceIdentity | None
    disposition: ObservationDisposition
    winner: ObservationRef | None = None

    def __post_init__(self) -> None:
        if ((self.disposition is ObservationDisposition.SUPPRESSED_DUPLICATE)
                != (self.winner is not None)):
            raise ValueError("only a suppressed observation has a winner")


@dataclass
class BatchQueryResult:
    request: BatchQuery
    status: QueryStatus
    result: SearchResult | None = None
    error: QueryFailure | None = None
    export_indices: list[int] = field(default_factory=list)
    suppressed: list[DuplicateReference] = field(default_factory=list)
    unverified_identity_indices: list[int] = field(default_factory=list)
    observations: tuple[ObservationProvenance, ...] = ()
    execution_time: float = 0.0

    def __post_init__(self) -> None:
        if type(self.status) is not QueryStatus:
            raise TypeError("status must be a QueryStatus")
        if self.status is QueryStatus.FAILED:
            if (self.result is not None or self.error is None or self.export_indices
                    or self.suppressed or self.unverified_identity_indices or self.observations):
                raise ValueError("failed query must contain only a safe failure")
            return
        if self.result is None or self.error is not None:
            raise ValueError("valid query must contain a result and no failure")
        count = self.result.total_found
        exported = self.export_indices
        suppressed = [item.duplicate.business_index for item in self.suppressed]
        if any(type(index) is not int or index < 0 or index >= count for index in exported + suppressed):
            raise ValueError("selection index out of range")
        if exported != sorted(set(exported)):
            raise ValueError("export indices must be ordered and unique")
        if len(exported) + len(suppressed) != count or set(exported) & set(suppressed) or len(set(suppressed)) != len(suppressed):
            raise ValueError("each observation must be classified exactly once")
        if any(index not in exported for index in self.unverified_identity_indices):
            raise ValueError("unverified indices must be exportable")
        if self.unverified_identity_indices != sorted(set(self.unverified_identity_indices)):
            raise ValueError("unverified indices must be ordered and unique")
        if self.observations and len(self.observations) != count:
            raise ValueError("provenance must cover every observation")
        if self.observations:
            for index, observation in enumerate(self.observations):
                if observation.observation.business_index != index:
                    raise ValueError("provenance order must match the result")
                if (observation.disposition is ObservationDisposition.SUPPRESSED_DUPLICATE) != (index in suppressed):
                    raise ValueError("provenance disposition conflicts with selection")
                if (observation.disposition is ObservationDisposition.IDENTITY_UNVERIFIED_EXPORTED) != (index in self.unverified_identity_indices):
                    raise ValueError("unverified provenance conflicts with selection")

    @property
    def observed_count(self) -> int:
        return self.result.total_found if self.result is not None else 0

    @property
    def exportable_count(self) -> int:
        return len(self.export_indices)

    @property
    def suppressed_count(self) -> int:
        return len(self.suppressed)


@dataclass
class BatchSearchResult:
    entries: list[BatchQueryResult] = field(default_factory=list)
    execution_time: float = 0.0

    @property
    def total_observations(self) -> int:
        return sum(entry.observed_count for entry in self.entries)

    @property
    def total_exportable(self) -> int:
        return sum(entry.exportable_count for entry in self.entries)

    @property
    def duplicates_suppressed(self) -> int:
        return sum(entry.suppressed_count for entry in self.entries)

    @property
    def total_unverified(self) -> int:
        return sum(len(entry.unverified_identity_indices) for entry in self.entries)

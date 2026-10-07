"""Identity value contract; verification is owned by the source pipeline."""

from dataclasses import dataclass
from enum import Enum

from models.search_query import Source


@dataclass(frozen=True)
class VerifiedSourceIdentity:
    """A namespaced value, not proof that a source token was verified."""

    source: Source
    kind: str
    value: str

    def __post_init__(self) -> None:
        if type(self.source) is not Source:
            raise TypeError("identity source must be a Source")
        if type(self.kind) is not str or not self.kind:
            raise ValueError("identity kind must be a nonempty string")
        if type(self.value) is not str or not self.value:
            raise ValueError("identity value must be a nonempty string")


class VerificationState(str, Enum):
    VERIFIED = "verified"
    UNVERIFIED = "unverified"


@dataclass(frozen=True)
class SourceIdentityEvidence:
    """One safe, positional source observation; no commercial fields."""

    verified: VerifiedSourceIdentity | None
    verification_state: VerificationState
    reason: str

    def __post_init__(self) -> None:
        if (self.verified is not None) != (self.verification_state is VerificationState.VERIFIED):
            raise ValueError("verification state must match identity evidence")

    @classmethod
    def unverified(cls, reason: str = "identity_unavailable") -> "SourceIdentityEvidence":
        return cls(None, VerificationState.UNVERIFIED, reason)

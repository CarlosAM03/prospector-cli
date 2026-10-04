"""Public, safe record of a recoverable search problem."""

from dataclasses import dataclass


@dataclass(frozen=True)
class SearchIssue:
    stage: str
    code: str
    message: str
    candidate: str | None = None
    exception_type: str | None = None

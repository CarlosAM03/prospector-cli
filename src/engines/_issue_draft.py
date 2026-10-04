"""Internal issue transport draft; public v0.7.5 schema awaits ratification."""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class _IssueDraft:
    stage: str
    reason: str
    candidate: str | None = None
    exception_type: str | None = None


@dataclass
class _IssueCollector:
    items: list[_IssueDraft] = field(default_factory=list)

    def record(
        self,
        stage: str,
        reason: str,
        *,
        candidate: str | None = None,
        error: Exception | None = None,
    ) -> None:
        self.items.append(
            _IssueDraft(
                stage=stage,
                reason=reason,
                candidate=candidate,
                exception_type=type(error).__name__ if error else None,
            )
        )

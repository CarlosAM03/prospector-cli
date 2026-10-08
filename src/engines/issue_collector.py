"""Per-execution collection of approved public recoverable issues."""

from models.search_issue import SearchIssue
from engines._observability import ExecutionEvent, emit


_MESSAGES = {
    ("detail", "identity_unverifiable"):
        "Detail identity could not be verified; summary data was preserved.",
    ("detail", "target_unavailable"):
        "The exact detail candidate was unavailable; summary data was preserved.",
    ("detail", "click_unavailable"):
        "Detail selection was unavailable; summary data was preserved.",
    ("detail", "panel_unavailable"):
        "Detail information was unavailable; summary data was preserved.",
    ("detail", "fields_unverifiable"):
        "Detail fields could not be verified; summary data was preserved.",
    ("website", "inspection_unavailable"):
        "Website enrichment was unavailable; existing business data was preserved.",
    ("feed", "partial_results"):
        "The result feed stopped before the requested limit; available businesses were preserved.",
    ("normalization", "field_unverifiable"):
        "A business field could not be normalized safely; its original value was preserved.",
    ("normalization", "field_unavailable"):
        "A controlled normalization operation was unavailable; its original value was preserved.",
}


class IssueCollector:
    """Never stores exception text, URLs, secrets or browser state in issues."""

    def __init__(self) -> None:
        self.items: list[SearchIssue] = []

    def record(
        self,
        stage: str,
        code: str,
        *,
        candidate: str | None = None,
        error: Exception | None = None,
    ) -> None:
        issue = SearchIssue(
                stage=stage,
                code=code,
                message=_MESSAGES.get(
                    (stage, code), "A recoverable search issue occurred."
                ),
                candidate=candidate,
                exception_type=type(error).__name__ if error else None,
            )
        self.items.append(issue)
        emit(ExecutionEvent("recoverable_issue_observed", stage=stage, name=code))

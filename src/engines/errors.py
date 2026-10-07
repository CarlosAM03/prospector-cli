"""Minimal typed fatal categories at the reusable Engine boundary."""


class ProspectorError(Exception):
    """Fatal error for a search execution."""


class ProspectorConfigurationError(ProspectorError):
    """The requested Engine configuration is invalid or unavailable."""


class ProspectorNavigationError(ProspectorError):
    """Navigation did not reach a usable source state."""


class ProspectorExtractionError(ProspectorError):
    """The source could not produce a valid search outcome."""


class ProspectorSourceError(ProspectorExtractionError):
    """The requested source is unsupported."""

class ProspectorRuntimeError(ProspectorError):
    """The owned browser runtime could not start or close."""

class BatchInterruptedError(ProspectorError):
    """A critical batch failure; only completed entries are recoverable."""

    def __init__(
        self, *, completed, interrupted_query_index: int,
        reason_code: str, remaining_query_indices: tuple[int, ...],
    ) -> None:
        super().__init__("Batch execution was interrupted; remaining queries were not run.")
        self.completed = completed
        self.interrupted_query_index = interrupted_query_index
        self.reason_code = reason_code
        self.remaining_query_indices = remaining_query_indices

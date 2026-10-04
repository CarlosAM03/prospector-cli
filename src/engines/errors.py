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

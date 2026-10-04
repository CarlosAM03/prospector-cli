"""Reusable facade for the approved Google Maps extraction strategy."""

from engines.config import EngineConfig, GOOGLE_MAPS_ENGINE_MAX_LIMIT, resolve_limit
from engines.errors import ProspectorConfigurationError, ProspectorSourceError
from models.search_query import SearchQuery, Source
from models.search_result import SearchResult
from scraper.google_maps.scraper import _run_google_maps


class ProspectorEngine:
    """Reusable extraction entrypoint, independent of CLI and ExportService."""

    # Owner-approved operational policy; not a claim of universal capacity.
    ENGINE_MAX_LIMIT = GOOGLE_MAPS_ENGINE_MAX_LIMIT

    def __init__(self, config: EngineConfig) -> None:
        if not isinstance(config, EngineConfig):
            raise TypeError("config must be an EngineConfig")
        self.config = config

    def search(self, query: SearchQuery) -> SearchResult:
        if not isinstance(query, SearchQuery):
            raise TypeError("query must be a SearchQuery")
        if query.source != Source.GOOGLE_MAPS:
            raise ProspectorSourceError("The requested source is unsupported.")
        try:
            limit = resolve_limit(
                self.config, engine_max_limit=self.ENGINE_MAX_LIMIT
            )
        except (ValueError, RuntimeError) as error:
            raise ProspectorConfigurationError(str(error)) from error
        return _run_google_maps(
            query, limit,
            headless=self.config.headless,
            website_enrichment=self.config.website_enrichment,
            typed_errors=True,
        )

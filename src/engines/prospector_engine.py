"""Contract-neutral facade for the approved Google Maps extraction strategy.

The operational maximum and public error schema still require approval.
Production searches through this facade reject an unset maximum explicitly.
"""

from engines.config import EngineConfig, resolve_limit
from models.search_query import SearchQuery, Source
from models.search_result import SearchResult
from scraper.google_maps.scraper import _run_google_maps


class ProspectorEngine:
    """Reusable extraction entrypoint, independent of CLI and ExportService."""

    # The owner must approve a value or equivalent determinable policy.
    ENGINE_MAX_LIMIT: int | None = None

    def __init__(self, config: EngineConfig) -> None:
        if not isinstance(config, EngineConfig):
            raise TypeError("config must be an EngineConfig")
        self.config = config

    def search(self, query: SearchQuery) -> SearchResult:
        if not isinstance(query, SearchQuery):
            raise TypeError("query must be a SearchQuery")
        if query.source != Source.GOOGLE_MAPS:
            # A finalized typed source error awaits v0.7.5 schema approval.
            raise NotImplementedError(f"unsupported source: {query.source}")
        limit = resolve_limit(
            self.config, engine_max_limit=self.ENGINE_MAX_LIMIT
        )
        return _run_google_maps(
            query, limit,
            headless=self.config.headless,
            website_enrichment=self.config.website_enrichment,
        )

"""Reusable facade for the approved Google Maps extraction strategy."""

from collections.abc import Sequence
import time

from engines.config import EngineConfig, GOOGLE_MAPS_ENGINE_MAX_LIMIT, resolve_limit
from engines._observability import ExecutionEvent, emit
from engines.batch import select_batch_exports
from engines.errors import (
    BatchInterruptedError, ProspectorConfigurationError, ProspectorExtractionError,
    ProspectorNavigationError, ProspectorSourceError,
)
from engines.global_pipeline import execute_global_search, execute_global_search_with_identities
from models.batch import (
    BatchQuery, BatchQueryResult, BatchSearchResult, ObservationDisposition,
    ObservationProvenance, ObservationRef, QueryFailure, QueryStatus,
)
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

    def _preflight_batch(self, queries: Sequence[BatchQuery]) -> tuple[BatchQuery, ...]:
        """Validate and snapshot every request before any source execution."""
        if not isinstance(queries, Sequence) or isinstance(queries, (str, bytes, bytearray)):
            raise ProspectorConfigurationError("Batch requests must be an ordered sequence.")
        if not 1 <= len(queries) <= 5:
            raise ProspectorConfigurationError("Batch requires between one and five queries.")
        try:
            EngineConfig(
                limit=self.config.limit, headless=self.config.headless,
                website_enrichment=self.config.website_enrichment,
            )
        except ValueError as error:
            raise ProspectorConfigurationError("Batch EngineConfig is invalid.") from error
        try:
            resolve_limit(self.config, engine_max_limit=self.ENGINE_MAX_LIMIT)
        except (ValueError, RuntimeError) as error:
            raise ProspectorConfigurationError(str(error)) from error
        snapshot = []
        for request in queries:
            if type(request) is not BatchQuery or not isinstance(request.query, SearchQuery):
                raise ProspectorConfigurationError("Batch request has an invalid type.")
            source = request.query.source
            keyword = request.query.keyword
            location = request.query.location
            if type(source) is not Source or source is not Source.GOOGLE_MAPS:
                raise ProspectorSourceError("The requested source is unsupported.")
            if type(keyword) is not str or type(location) is not str:
                raise ProspectorConfigurationError("Batch query text must be strings.")
            if type(request.limit) is not int:
                raise ProspectorConfigurationError("Batch limit must be an integer.")
            try:
                limit = resolve_limit(
                    self.config, requested_limit=request.limit,
                    engine_max_limit=self.ENGINE_MAX_LIMIT,
                )
            except (ValueError, RuntimeError) as error:
                raise ProspectorConfigurationError(str(error)) from error
            snapshot.append(BatchQuery(SearchQuery(source, keyword, location), limit))
        return tuple(snapshot)

    def search_many(self, queries: Sequence[BatchQuery]) -> BatchSearchResult:
        """Execute a validated batch in order with one closed runtime per query."""
        requests = self._preflight_batch(queries)
        started = time.perf_counter()
        entries: list[BatchQueryResult] = []
        for query_index, request in enumerate(requests):
            emit(ExecutionEvent("execution_started", "query", query_index=query_index))
            emit(ExecutionEvent("metric_updated", name="requested_limit", value=request.limit, query_index=query_index))
            query_started = time.perf_counter()
            try:
                execution = execute_global_search_with_identities(
                    _run_google_maps, request.query, request.limit,
                    headless=self.config.headless,
                    website_enrichment=self.config.website_enrichment,
                    typed_errors=True,
                )
                result = execution.result
                if (result.query.source, result.query.keyword, result.query.location) != (
                    request.query.source, request.query.keyword, request.query.location,
                ):
                    raise ValueError("batch source returned a different query")
                observations = tuple(
                    ObservationProvenance(
                        ObservationRef(query_index, index), evidence.verified,
                        ObservationDisposition.EXPORTED if evidence.verified is not None
                        else ObservationDisposition.IDENTITY_UNVERIFIED_EXPORTED,
                    )
                    for index, evidence in enumerate(execution.identities)
                )
                status = (
                    QueryStatus.PARTIAL if any(
                        issue.stage == "feed" and issue.code == "partial_results"
                        for issue in result.issues
                    ) else QueryStatus.SUCCESS_WITH_ISSUES if result.issues
                    else QueryStatus.SUCCESS
                )
                completed_entry = BatchQueryResult(
                    request=request, status=status, result=result,
                    export_indices=list(range(result.total_found)),
                    unverified_identity_indices=[
                        index for index, evidence in enumerate(execution.identities)
                        if evidence.verified is None
                    ],
                    observations=observations, execution_time=result.execution_time,
                )
                emit(ExecutionEvent("stage_started", "deduplication", query_index=query_index))
                entries = select_batch_exports(
                    BatchSearchResult([*entries, completed_entry]),
                ).entries
                emit(ExecutionEvent("stage_completed", "deduplication", query_index=query_index))
                entry = entries[-1]
                emit(ExecutionEvent("metric_updated", name="duplicates_suppressed", value=entry.suppressed_count, query_index=query_index))
                emit(ExecutionEvent("metric_updated", name="exportable_businesses", value=entry.exportable_count, query_index=query_index))
                emit(ExecutionEvent("execution_completed", "query", query_index=query_index))
            except (ProspectorNavigationError, ProspectorExtractionError) as error:
                if getattr(error, "_prospector_cleanup_failed", False):
                    self._interrupt_batch(
                        entries, started, query_index, len(requests),
                        "cleanup_failed", error,
                    )
                category = "navigation" if isinstance(error, ProspectorNavigationError) else "extraction"
                entries.append(BatchQueryResult(
                    request=request, status=QueryStatus.FAILED,
                    error=QueryFailure(
                        category, "The source could not complete this query.",
                        type(error).__name__,
                    ),
                    execution_time=time.perf_counter() - query_started,
                ))
                emit(ExecutionEvent("execution_failed", "query", query_index=query_index))
            except Exception as error:
                self._interrupt_batch(
                    entries, started, query_index, len(requests),
                    "critical_failure", error,
                )
        result = BatchSearchResult(entries, time.perf_counter() - started)
        emit(ExecutionEvent("metric_updated", name="batch_execution_seconds", value=result.execution_time))
        emit(ExecutionEvent("execution_completed", "batch"))
        return result

    @staticmethod
    def _interrupt_batch(
        entries: list[BatchQueryResult], started: float,
        index: int, count: int, reason_code: str, error: Exception,
    ) -> None:
        raise BatchInterruptedError(
            completed=BatchSearchResult(list(entries), time.perf_counter() - started),
            interrupted_query_index=index, reason_code=reason_code,
            remaining_query_indices=tuple(range(index + 1, count)),
        ) from error

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
        emit(ExecutionEvent("execution_started", "query"))
        emit(ExecutionEvent("metric_updated", name="requested_limit", value=limit))
        try:
            result = execute_global_search(
                _run_google_maps, query, limit,
                headless=self.config.headless,
                website_enrichment=self.config.website_enrichment,
                typed_errors=True,
            )
        except Exception:
            emit(ExecutionEvent("execution_failed", "query"))
            raise
        emit(ExecutionEvent("metric_updated", name="exportable_businesses", value=result.total_found))
        emit(ExecutionEvent("execution_completed", "query"))
        return result

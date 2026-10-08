# P101 metrics inventory — R03 groundwork

`_run_google_maps(..., metrics_sink: dict | None)` currently records `browser_version`, `navigation_seconds`, `feed_seconds`, `observed_candidates`, `detail_seconds`, `detail_unchanged_count`, optional `website_seconds`, and `cleanup_completed`. Values are local to source execution and not yet surfaced to the CLI. Stage seconds use `time.perf_counter()` and are measured only after stage completion. `observed_candidates` currently equals `len(results)` returned by `extract_businesses`, so it must **not** be advertised as all Google Maps candidates observed without further proof; `Business` extraction is a distinct count.

P102 must reconcile this sink with neutral internal events and classify requested limit, candidates observed, extracted, normalized, verified/unverified, suppressed, exportable, recoverable issues, query/batch time and stage times as EXACT, DERIVED or UNAVAILABLE. No user metric is approved merely because a desired label appears in ADR-010.

## P102 implemented semantics

The private `engines._observability` ContextVar binds one synchronous callback without changing public Engine signatures. No listener is valid; listener exceptions are logged and cannot alter a SearchResult. The existing `metrics_sink` remains a low-level optional dict in the Google Maps source; each historical sink write now emits the same neutral metric event, so there is one measurement path rather than a competing collector. `result_list` additionally counts distinct href-bearing candidate cards actually visited by the feed loop. This is **not** a Maps catalog-total claim. Rich is absent from Engine/source/models.

| UX metric | Classification | Exact meaning / owner |
|---|---|---|
| `requested_limit` | EXACT | Validated per-query Engine requested limit |
| `maps_candidates_observed` | EXACT | Distinct href-bearing cards seen by the running feed traversal; not source total |
| `businesses_extracted` | EXACT | Consolidated `Business[]` length after source enrichment |
| `businesses_normalized` | EXACT | `NormalizedBusiness[]` length after one global normalization |
| `verified_identities` | DERIVED | Count of aligned non-null verified identities |
| `unverified_identities` | DERIVED | Count of aligned null identity evidence |
| `duplicates_suppressed` | EXACT | Batch selector's per-query suppressed count; not a single-query metric |
| `exportable_businesses` | EXACT | Normalized count for single; batch-selected count after dedupe for batch |
| `recoverable_issue_count` | DERIVED | `len(SearchResult.issues)` after source plus normalization |
| `query_execution_seconds` | EXACT | `SearchResult.execution_time`, monotonic elapsed source + normalization |
| `batch_execution_seconds` | EXACT | `BatchSearchResult.execution_time`, monotonic batch elapsed |
| `navigation_seconds`, `feed_seconds`, `detail_seconds`, `website_seconds` | EXACT when emitted | `time.perf_counter()` delta per completed source stage; omitted when stage not completed/disabled |

The legacy `observed_candidates` sink value remains `len(results)` for compatibility, but it is **not** shown as Maps candidates observed. Feed progress carries valid Business count without a fabricated total. Source failures can omit metrics from incomplete stages. The CLI must not display unavailable values as zero.

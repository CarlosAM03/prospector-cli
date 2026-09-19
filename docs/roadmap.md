# Roadmap

This roadmap distinguishes historical milestones, current capabilities and future targets. The remaining stabilization work is intentionally described at the `v0.7.x` line level; patch-version decomposition is deferred.

## Historical milestones — HISTORICAL

The project history includes bootstrap, Google Maps navigation, business/detail extraction, export, selector infrastructure and Website Engine work. Historical descriptions do not override the current source. References to normalization, single-evaluation extraction, automatic pagination or configuration profiles must not be read as proof that those capabilities are complete now.

### Historical evolution

The earlier roadmap and commits record this sequence of development:

- `v0.1.x`: repository bootstrap, Playwright integration, initial Google Maps navigation, interactive queries and browser validation.
- `v0.2.x`: initial result-list fields and the first internal business models.
- `v0.3.x`: detail-panel extraction, incremental enrichment and website discovery, followed by performance/synchronization work.
- `v0.4.x`: `SearchResult`, exporter interfaces, file naming and CSV/XLSX export integration.
- `v0.5.x`: selector profiles, registry, selector resolution and candidate-election/fallback infrastructure.
- `v0.6.x`: Website crawler/parser/extractor integration as a separate enrichment phase.
- Early `v0.7.0`: Navigation Engine integration and lazy/dynamic-content support for the Google Maps pipeline.

These are historical milestones and architectural context. Some old objective wording, such as “normalization” or “pagination”, has been reclassified by the current baseline because the present implementation and approved plan use more precise boundaries.

## Current checkpoint — CURRENT

Phase 0 — baseline audit and Phase 1 — regression safety are complete. The permanent suite has deterministic unit tests, controlled integration tests and an opt-in live Google Maps E2E check. The default suite does not require Internet or reach Google Maps.

The application remains a CLI-first Google Maps pipeline with Website Engine enrichment and CSV/XLSX export. `ProspectorEngine` and `EngineConfig` do not yet exist.

## v0.7.x — TARGET_V0_7_X

The stabilization line covers:

1. Google Maps feed readiness, virtual/infinite scrolling, detail identity and partial prospect behavior;
2. extraction of the initial public/internal configuration boundary;
3. explicit Playwright/browser lifecycle ownership and cleanup;
4. separation of engine diagnostics from CLI output;
5. recoverable/fatal error semantics and structured partial-result evidence;
6. an internal `ProspectorEngine(config).search(query)` facade;
7. migration of the CLI to consume that facade.

The exact patch-version decomposition is deferred and is not defined here.

## v0.8.x — TARGET_V0_8

One primary concern: formal deterministic normalization after extraction/enrichment. Deduplication is not part of this boundary.

## v0.9.x — TARGET_V0_9

Multiple SearchQuery inputs plus deduplication, merge, batch-result semantics and measured execution/performance decisions. Browser strategy, identity confidence, concurrency and query-level partial outcomes remain future design work.

## v1.0.0 — TARGET_V1_0

The first complete and stable release should provide a stable CLI, stable Engine contract, documented current behavior, regression safety, appropriate error/configuration semantics and extraction-ready internal architecture. Physical extraction into a separate package is not required before `v1.0.0`.

## Post-v1 — POST_V1

Possible later work includes physical Prospector Engine packaging, additional source adapters/exporters, plugins and distributed or parallel execution. These are future extensions, not current capabilities.

Prospector CLI remains an independent open-source CLI project, not a SaaS, API, or distributed service.

# Roadmap

This roadmap distinguishes historical milestones, owner-accepted capabilities and future targets. v0.9.x is functionally complete on implementation baseline `c7193d55a36618e934e29a9678b3f9b01e9b6543`; no tag or release is claimed.

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

Phase 0 — baseline audit, Phase 1 — regression safety, and controlled Google Maps hardening are complete in source. The permanent suite has deterministic unit tests, controlled integration tests and an opt-in live Google Maps E2E check. The default suite remains offline. A separately authorized C05 pilot ran three of eight planned combinations and stopped at the 180-second hard timeout on the third.

The application remains a CLI-first Google Maps pipeline with Website Engine enrichment and CSV/XLSX export. `BrowserRuntime` owns per-search resources; `SearchResult.issues` and typed fatal errors are implemented. The CLI calls `ProspectorEngine` with an optional requested limit defaulting to 50 and rejects values above the owner-approved Google Maps maximum of 100 before browser access. The legacy wrapper remains available without that new cap. Both paths now pass through the shared normalization stage and expose normalized plus original results. The earlier C05 pilot exposed detail problems; later corrections have deterministic offline coverage. The owner subsequently completed manual CLI searches and exports at limits 75 and 50 on the v0.7.x baseline. Those earlier runs alone did not establish v0.8.x acceptance, full-pipeline capacity at 100 or source catalog completeness; the later v0.8.x functional acceptance is recorded below with its N31 caveat. Commit `ee6b69e` remains the accepted v0.7.x functional baseline; no v0.8.x release tag is claimed.

## v0.7.x — CURRENT ACCEPTED BASELINE

The stabilization line covers:

1. Google Maps feed readiness, virtual/infinite scrolling, detail identity and partial prospect behavior;
2. extraction of the initial public/internal configuration boundary;
3. explicit Playwright/browser lifecycle ownership and cleanup;
4. separation of engine diagnostics from CLI output;
5. recoverable/fatal error semantics and structured partial-result evidence;
6. an internal `ProspectorEngine(config).search(query)` facade;
7. migration of the CLI to consume that facade.

The approved Master Plan defines the patch sequence; this roadmap records only verified current behavior and line-level targets.

## v0.8.x — OWNER ACCEPTED / COMPLETE

Deterministic, mandatory normalization follows extraction/enrichment. `SearchResult` exposes independent normalized and consolidated original views; CLI and CSV/XLSX consume normalized values. The owner accepted v0.8.0 functionally with an explicit N31 caveat: paired live inspection of `Business` and `NormalizedBusiness` from the same execution was not performed. Their correspondence, preservation and independence were verified offline; do not record paired live N31 as PASS. Deduplication is outside this boundary.

## v0.9.x — OWNER ACCEPTED / COMPLETE

The accepted implementation provides bounded sequential `search_many()` execution, typed per-query outcomes, positional identity evidence, exact interquery deduplication of verified Google Place IDs and separate seven-column CSV/XLSX exports. P91–P96 and G01–G22 passed offline. The narrow P92 identity study was distinct from the owner's two later full CLI batches, which are accepted as **G23 PASS / OWNER LIVE ACCEPTED**. The owner accepts that `UNVERIFIED` observations remain exportable and may yield apparent commercial duplicates. No field merge, heuristic matching, persistence, campaigns, concurrency or new sources are part of this line. This is a development-cycle closure, not a release.

## v1.0.0 — NEXT / FINAL HARDENING AND STABLE RELEASE

The next phase is limited to final hardening, stability, contract freeze, final validation, user documentation, packaging/distribution and preparation of the first stable CLI release. An `.exe` or installer may be considered during that phase, but neither exists by this closure. Physical Engine extraction and API consumers remain post-v1 possibilities, not prerequisites for the CLI's first stable release.

## Post-v1 — POST_V1

Possible later work includes physical Prospector Engine packaging, additional source adapters/exporters, plugins and distributed or parallel execution. These are future extensions, not current capabilities.

Prospector CLI remains an independent open-source CLI project, not a SaaS, API, or distributed service.

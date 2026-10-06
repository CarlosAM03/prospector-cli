# Architecture

This document separates the architecture implemented in the local worktree from future direction. v0.8.x is verified offline and awaits owner acceptance.

## Architectural Philosophy

The repository evolved toward an engine-based organization so source-specific extraction can use reusable navigation, selector, synchronization, website and export components. The design goal is not to claim that every future source or consumer already exists; it is to keep responsibilities explicit so additional strategies can be introduced without coupling them to the CLI.

The governing principles are simplicity, single responsibility, reusability, source-specific pipelines, incremental enrichment, and configuration over hardcoded behavior where configuration is actually available. A reusable design scope and a current consumer are different facts: one current consumer does not make an abstraction source-exclusive, and a reusable abstraction does not prove that multiple sources already use it.

## Architectural Principles

- Reusable behavior should exist in one appropriate shared place rather than being duplicated across source pipelines.
- Engines coordinate reusable execution behavior or infrastructure.
- Utilities provide focused helper behavior and should remain stateless where practical.
- A scraper/source pipeline owns behavior specific to one public source or acquisition strategy.
- Reusable infrastructure should not depend on a concrete scraper; source-specific code may depend on reusable infrastructure when that infrastructure applies.
- Extraction, presentation and export remain separate concerns.

This is architectural intent, not a claim that every target boundary has already been implemented.

## Dependency Principles

The intended dependency direction is:

```text
consumer / CLI
        |
        v
reusable boundary and domain models
        |
        v
source-specific pipeline
        |
        v
external browser, network or parsing libraries
```

The CLI calls `ProspectorEngine`, which delegates to the Google Maps source pipeline and then the shared normalization stage. The owner-approved Engine maximum is 100; invalid requests are rejected before browser startup. The legacy `search_businesses` wrapper retains its input policy and uses the same normalization stage.

### Engine, utility and scraper

An **Engine** coordinates reusable execution behavior or infrastructure, such as navigation, selector resolution, dynamic-content synchronization or website inspection. A **utility** provides a focused helper, such as parsing or file naming. A **scraper/source pipeline** implements the extraction workflow specific to a source or access strategy. One current consumer is sufficient to justify reusable design scope, but reuse must not be claimed as multiple-source usage without evidence.

## Current architecture — CURRENT

```text
main.py
  -> SearchQuery
  -> EngineConfig(limit=interactive value or 50)
  -> ProspectorEngine.search(query)
       -> BrowserRuntime -> Playwright / Chromium
       -> NavigationEngine -> GoogleMapsNavigation
       -> Google Maps virtual/infinite feed loading
       -> summary parser -> ordered Business[]
       -> detail-panel identity validation and enrichment
       -> Website Engine enrichment
       -> consolidated Business[]
       -> global normalization -> NormalizedBusiness[]
       -> SearchResult (normalized + original + issues)
  -> ExportService -> CSV/XLSX

legacy Python caller -> search_businesses(query, limit=50)
                   -> same Google Maps source pipeline and normalization
```

The `search_businesses(query, limit)` function remains a transitional compatibility boundary. It does not impose the new EngineConfig maximum retroactively.

### Current components

`main.py` owns interactive input, query construction, Engine invocation, user-facing results/issues/errors and export selection. It does not orchestrate Google Maps extraction stages.

`src/models/` contains `Business`, `NormalizedBusiness`, `SearchQuery`, `SearchResult`, `WebsiteDocument` and `WebsiteMetadata`. `Business` is mutable and may be partially enriched. `SearchResult.businesses` contains ordered `NormalizedBusiness` objects and `original_businesses` contains their matching consolidated originals; query, complete execution time, issues and `total_found` are preserved.

`NavigationEngine` delegates Google Maps navigation to `GoogleMapsNavigation`. Selector registry/elector/selector infrastructure provides lookup and fallback behavior; concrete DOM selectors remain source-specific.

`src/scraper/google_maps/` coordinates feed loading, summary parsing, detail identity validation and website enrichment. `BrowserRuntime` owns Playwright, the browser and Maps pages for each execution. WebsiteCrawler closes its short-lived inspection pages.

`EngineConfig` validates a requested limit, headless mode and optional website enrichment. The separate Google Maps Engine maximum is 100, while the CLI default is 50. A per-execution collector propagates recoverable feed, detail, website and normalization issues into `SearchResult.issues`. Fatal Engine errors use typed `ProspectorError` categories with chained causes.

`src/engines/normalization/` owns pure field rules and field-level recovery. `src/engines/global_pipeline.py` runs the source once, normalizes once and assembles both representations. The Google Maps source still owns navigation, candidate identity, extraction and enrichment.

`src/engines/website/` contains crawling, parsing, extraction, email extraction, language detection and metadata construction. Basic status/final URL, title, description, language and email behavior is covered by controlled tests. Contact/about flags and effective `content_type` output remain incomplete.

`ExportService` consumes `SearchResult` and writes CSV/XLSX. It is reusable application/export infrastructure, outside extraction core and not CLI-only.

### Reusable design scope versus current usage

| Component | Design scope | Current usage |
| --- | --- | --- |
| `NavigationEngine` | A navigation boundary that can select a source-specific navigation strategy | Google Maps navigation |
| `SelectorEngine` | Semantic selector resolution through registered profiles | Google Maps selectors and selector tests |
| `ElectorEngine` | Candidate selection/fallback behavior for selectors | Selector infrastructure used by the current pipeline |
| `LazyChargeEngine` | Reusable synchronization for dynamically rendered/lazy/virtual content; it does not parse page content | Google Maps feed/detail synchronization support |
| `WebsiteEngine` | Reusable website inspection and metadata enrichment | Google Maps website enrichment |
| `ExportService` | Reusable conversion of `SearchResult` to application output formats | Current CLI CSV/XLSX flow |
| Models | Shared result/domain contracts | Current Google Maps and Website paths |

Google Maps is the only implemented/supported prospect source today. The abstractions are structured so future source strategies may reuse them when their behavior requires it; no additional source is currently claimed.

## Current technical debt — TECHNICAL_DEBT

Remaining technical debt includes source-specific selector/URL assumptions, incomplete contact/about/content type metadata and unverified source-end detection. The earlier C05 pilot returned 3 and 10 Businesses with summary data only; a 25 request hit its 180-second hard timeout. After the corrective refactor, the owner completed two manual searches and exports at limits 75 and 50. Those searches demonstrate operation for their queries, not a certified capacity or catalog completeness. The approved maximum of 100 remains an owner policy. Reusable components use module loggers without setting global logging policy; CLI presentation remains in `main.py`.

## Implemented v0.7.x boundary — CURRENT / TARGET_V1_0

```text
CLI adapter       other Python consumer / future API
       \                         /
        +---- ProspectorEngine(config) ----+
                                         |
                                  extraction pipeline
                                         |
                                    SearchResult
                                         |
                                   ExportService
                                      /      \
                                    CSV      XLSX
```

The v0.7.x boundary means the Engine owns reusable prospecting orchestration; the CLI owns input/presentation; and `ExportService` consumes `SearchResult` without belonging inside extraction core. These boundaries, the approved Error Model and the approved maximum policy are implemented. `output_path` remains outside EngineConfig. Commit `ee6b69e` is the accepted technical baseline for formal v0.8.0 planning; no release tag is implied.

## Version boundaries

- `v0.7.x` — `TARGET_V0_7_X`: Google Maps stability, configuration boundary, browser lifecycle, logging separation, error/partial semantics, internal Engine facade and CLI adapter.
- `v0.8.x` — `CURRENT, OWNER_ACCEPTANCE_PENDING`: deterministic field normalization after extraction/enrichment, verified offline.
- `v0.9.x` — `TARGET_V0_9`: multi-input, deduplication, merge and measured batch execution decisions.
- `v1.0.0` — `TARGET_V1_0`: stable CLI/Engine contracts, documented behavior, regression safety and extraction-ready architecture.
- post-v1 — `POST_V1`: possible physical Engine packaging/extraction, more sources/exporters or distributed execution.

Prospector CLI does not implement SaaS, a web API, CRM/ERP, a DATRA backend, jobs or distributed execution.

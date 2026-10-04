# Architecture

This document separates the architecture implemented today from the approved future direction. Future components are not available APIs.

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

The CLI now calls `ProspectorEngine`, which delegates to the Google Maps source pipeline. The operational maximum is not approved, so this route rejects searches before source I/O. The legacy `search_businesses` wrapper remains a separate compatibility entrypoint.

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
       -> SearchResult
  -> ExportService -> CSV/XLSX

legacy Python caller -> search_businesses(query, limit=50)
                   -> same Google Maps source pipeline
```

The `search_businesses(query, limit)` function remains a transitional compatibility boundary. It does not impose the new EngineConfig maximum retroactively.

### Current components

`main.py` owns interactive input, query construction, Engine invocation, user-facing results/issues/errors and export selection. It does not orchestrate Google Maps extraction stages.

`src/models/` contains `Business`, `SearchQuery`, `SearchResult`, `WebsiteDocument` and `WebsiteMetadata`. `Business` is mutable and may be partially enriched. `SearchResult` preserves query, ordered Businesses, execution time and `total_found`.

`NavigationEngine` delegates Google Maps navigation to `GoogleMapsNavigation`. Selector registry/elector/selector infrastructure provides lookup and fallback behavior; concrete DOM selectors remain source-specific.

`src/scraper/google_maps/` coordinates feed loading, summary parsing, detail identity validation and website enrichment. `BrowserRuntime` owns Playwright, the browser and Maps pages for each execution. WebsiteCrawler closes its short-lived inspection pages.

`EngineConfig` validates a requested limit, headless mode and optional website enrichment. The separate `engine_max_limit` policy is still unapproved, so the facade rejects normal searches until that policy is supplied. A per-execution collector propagates recoverable detail, website and partial-feed issues into the public `SearchResult.issues` list. Fatal Engine errors use typed `ProspectorError` categories with chained causes.

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

Remaining technical debt includes the unapproved Engine maximum, source-specific selector/URL assumptions, incomplete contact/about/content type metadata and live detail identity performance. The authorized C05 pilot returned 3 and 10 Businesses with summary data only; a 25 request hit its 180-second hard timeout, so no full-pipeline capacity maximum was established. Reusable components use module loggers without setting global logging policy; CLI presentation remains in `main.py`.

## Approved target architecture — TARGET_V0_7_X / TARGET_V1_0

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

The target means the Engine owns reusable prospecting orchestration; the CLI owns input/presentation; and `ExportService` consumes `SearchResult` without belonging inside extraction core. These boundaries and the approved Error Model are implemented. `output_path` remains outside EngineConfig. The Engine/CLI route is not operationally complete until the maximum policy is approved and validated.

## Version boundaries

- `v0.7.x` — `TARGET_V0_7_X`: Google Maps stability, configuration boundary, browser lifecycle, logging separation, error/partial semantics, internal Engine facade and CLI adapter.
- `v0.8.x` — `TARGET_V0_8`: deterministic field normalization after extraction/enrichment.
- `v0.9.x` — `TARGET_V0_9`: multi-input, deduplication, merge and measured batch execution decisions.
- `v1.0.0` — `TARGET_V1_0`: stable CLI/Engine contracts, documented behavior, regression safety and extraction-ready architecture.
- post-v1 — `POST_V1`: possible physical Engine packaging/extraction, more sources/exporters or distributed execution.

Prospector CLI does not implement SaaS, a web API, CRM/ERP, a DATRA backend, jobs or distributed execution.

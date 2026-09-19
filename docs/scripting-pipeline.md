# Scripting Pipeline

This page documents the flow implemented today. Future stages are listed separately and are not implied to be present.

The pipeline is intentionally described at two levels: reusable boundaries represent the design scope, while the current Google Maps path identifies the consumer that exists today. A future source may require a different internal sequence and may not need every current Google Maps synchronization component.

## Current flow — CURRENT

```text
Interactive CLI input
        |
        v
SearchQuery
        |
        v
search_businesses(query, limit)
        |
        v
Playwright / Chromium
        |
        v
NavigationEngine -> GoogleMapsNavigation
        |
        v
Google Maps virtual/infinite feed
        |
        v
Summary extraction -> ordered Business[]
        |
        v
Detail panel identity validation and enrichment
        |
        v
Website Engine enrichment when available
        |
        v
SearchResult
        |
        +--> CLI presentation
        |
        +--> ExportService -> CSV/XLSX
```

### Input and navigation

The current CLI asks for keyword and location and constructs a Google Maps `SearchQuery`. The interactive path calls the scraper with `limit=500`; the programmatic boundary accepts a query and limit. The scraper starts Playwright/Chromium and uses `NavigationEngine`/`GoogleMapsNavigation` to reach results.

### Feed and extraction

Google Maps results are loaded through a virtual/infinite feed with source-specific synchronization, scrolling and fixed timing values. The result-list stage parses summary information into ordered `Business` objects and retains identity information for the detail pass. `limit` bounds Businesses processed/returned, not DOM nodes loaded.

### Enrichment and result

The detail stage validates identity before applying available data. A detail failure can leave a partial Business. Website Engine may add basic status/final URL, title, description, language and email data. Website failure is recoverable at prospect level under the approved direction, but no structured issue schema exists yet.

`SearchResult` preserves query, ordered Businesses, `total_found` and execution time. Export is a subsequent operation through reusable `ExportService`.

## Not current

The source does not implement general configuration profiles, a Query Builder, formal normalization, general validation, deduplication, multi-input, structured logging, structured error/issues, `ProspectorEngine` or `EngineConfig`.

## Approved target — TARGET_V0_7_X / TARGET_V1_0

```text
CLI adapter / future consumer
        |
        v
ProspectorEngine(config).search(query)
        |
        v
Extraction and enrichment pipeline
        |
        v
SearchResult
        +--> CLI presentation
        +--> ExportService -> CSV/XLSX
```

Normalization belongs to `v0.8.x`; multiple inputs, deduplication and merge belong to `v0.9.x`. A future API is a possible consumer, not a current stage.

## Pipeline design principles

The project evolved around small stages with explicit inputs and outputs, incremental enrichment and source-specific extraction strategies. Navigation, selector resolution, dynamic-content synchronization, website inspection and export are separated so they can be reused where their behavior applies. Reuse is an architectural opportunity, not evidence that multiple sources currently consume every component.

## Future evolution — TARGET_V0_7_X / TARGET_V1_0 / POST_V1

The stabilization line is intended to place the current extraction flow behind `ProspectorEngine(config).search(query)` while keeping CLI presentation and `ExportService` outside the extraction core. `v0.8.x` adds formal normalization; `v0.9.x` adds multi-input, deduplication and merge decisions. Additional source strategies, API consumers and physical Engine packaging remain later possibilities and are not current pipeline stages.

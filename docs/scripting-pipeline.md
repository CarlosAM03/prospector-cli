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
ProspectorEngine.search / legacy search_businesses
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
consolidated Business[]
        |
        v
global normalization -> independent NormalizedBusiness[]
        |
        v
SearchResult (businesses + original_businesses + issues)
        |
        +--> CLI presentation
        |
        +--> ExportService -> CSV/XLSX
```

### Input and navigation

The current CLI asks for keyword, location and an optional positive limit (default 50, maximum 100), constructs a Google Maps `SearchQuery` and invokes `ProspectorEngine`. Invalid or over-maximum requests fail before browser access. The legacy `search_businesses(query, limit=50)` wrapper retains its historical input behavior. For a permitted source execution, `BrowserRuntime` starts Playwright/Chromium and provides the Maps page to `NavigationEngine`/`GoogleMapsNavigation`.

### Feed and extraction

Google Maps results are loaded through a virtual/infinite feed with source-specific synchronization, scrolling and fixed timing values. The result-list stage parses summary information into ordered `Business` objects and retains identity information for the detail pass. `limit` bounds Businesses processed/returned, not DOM nodes loaded.

### Enrichment and result

The detail stage requires a confirmed click, exact source place ID in the resulting URL and an equivalent title in the matching visible panel before applying available data. It keeps summaries if identity remains uncertain. Optional field reads avoid long waits for absent fields; a newly rendered field can legitimately share a previous Business's value. A numeric summary category that exactly repeats the available address's first segment is cleared as a source parsing artifact. Website Engine may add basic status/final URL, title, description, language and email data; percent-encoded `mailto:` links are decoded before email extraction. Inspection failure adds a recoverable issue without removing Maps data. A bounded feed stall with valid Businesses adds an issue. A verified source end would not; no reliable live end marker is currently established.

`SearchResult.businesses` contains ordered normalized objects and `original_businesses` contains corresponding consolidated source objects. `total_found` remains the extracted count; execution time includes normalization. Export is a subsequent operation through reusable `ExportService`.

## Not current

The source does not implement general configuration profiles, a Query Builder, business deduplication or multi-input. Global normalization, `EngineConfig`, module logging, the public Error Model and a CLI-connected `ProspectorEngine` exist. The owner-approved Google Maps maximum is 100. The two owner-run CLI searches and exports belong to the earlier v0.7.x baseline; v0.8.x owner acceptance remains separate.

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

## Architectural Pipeline Model

The broader project model can be understood as:

```text
input
  -> acquisition / source extraction
  -> incremental enrichment into Business[]
  -> global normalization into NormalizedBusiness[] [v0.8.x]
  -> SearchResult with both views
  -> consumers and export
  -> multi-input / deduplication [future v0.9.x]
```

This model shows the implemented v0.8.x boundary and the future v0.9.x scope. A source may use a browser, traditional HTML, an API or another public acquisition strategy; the shared result/domain boundary does not require reusing the Google Maps implementation.

## Pipeline design principles

The project evolved around small stages with explicit inputs and outputs, incremental enrichment and source-specific extraction strategies. Navigation, selector resolution, dynamic-content synchronization, website inspection and export are separated so they can be reused where their behavior applies. Reuse is an architectural opportunity, not evidence that multiple sources currently consume every component.

## Future evolution — TARGET_V0_7_X / TARGET_V1_0 / POST_V1

The extraction flow runs behind `ProspectorEngine(config).search(query)` while CLI presentation and `ExportService` remain outside the extraction core. `v0.8.x` adds the shared normalization stage; `v0.9.x` retains multi-input, deduplication and merge decisions. Additional source strategies, API consumers and physical Engine packaging remain later possibilities.

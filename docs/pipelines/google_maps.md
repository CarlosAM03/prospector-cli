# Google Maps Scraper Pipeline

This page documents the current Google Maps-specific pipeline and its known boundaries.

The pipeline was introduced as a source-specific multi-phase workflow: navigation, dynamic result preparation, identity registration, detail enrichment and website inspection. That separation explains the current module boundaries and remains useful design rationale even where individual synchronization techniques are still technical debt.

## Design Principles

The Google Maps pipeline applies the broader project principles through a source-specific strategy: separate phases, incremental enrichment, retained identity between passes and delegation to reusable infrastructure where applicable. These principles describe why the modules are separated; they do not require every future source to use Playwright, DOM selectors, SPA synchronization or `LazyChargeEngine`.

## Current pipeline — CURRENT

```text
SearchQuery
   |
   v
NavigationEngine -> GoogleMapsNavigation
   |
   v
Google Maps result feed
   |
   v
Virtual/infinite feed loading and scrolling
   |
   v
Summary parsing -> ordered Business[]
   |
   v
Detail panel -> identity validation -> enrichment
   |
   v
Website Engine enrichment
   |
   v
SearchResult
```

## Navigation

`NavigationEngine` is the access point used by the search stage. `GoogleMapsNavigation` opens Google Maps, enters the query and waits for the result view. It is source-specific; a generic multi-source navigation contract is not yet implemented.

## Result loading

Google Maps behaves as a single-page application with a virtual/infinite feed. The implementation waits for the feed and performs source-specific scrolling/loading work. `LazyChargeEngine` provides helpers, but the current result-list path still owns material scrolling and fixed timing behavior. Full delegation to a reusable synchronization abstraction is a `v0.7.x` target, not current fact.

`LazyChargeEngine` has a broader design scope than Google Maps alone: it provides semantic waiting, optional-selector handling and DOM-readiness coordination for dynamically rendered, lazy or virtual content. Google Maps is its current consumer because the Maps web application requires this kind of synchronization. Other sources may reuse it when their rendering strategy requires it, but no other source is currently implemented and not every future source would necessarily need it.

This is not formal page pagination. `limit` bounds Businesses processed/returned, while Google Maps may load a larger DOM batch. A run can therefore load six DOM results and return three Businesses for `limit=3` without violating the contract.

## Summary extraction

The first pass parses available name, category, address, phone and Maps href data into ordered `Business` objects. Identity is retained for later validation. Known parser mojibake is technical debt, not a desired contract.

## Detail enrichment

The detail stage opens a result, waits for panel state, validates identity and applies available fields. Concrete selectors, waits, URL assumptions and the exact browser extraction technique are implementation details, not architectural contracts. A failed detail operation may leave a valid partial Business in the output; no structured issue object exists yet.

The identity-first enrichment design exists to avoid associating a later panel state with the wrong result. The first pass retains stable information such as the extracted name and Maps href; subsequent phases validate the expected identity before mutating the same `Business` object. This is a design rationale, not a claim that all current synchronization is deterministic.

## Website enrichment

When a website is available, the scraper delegates inspection to Website Engine. Status/final URL, title, description, language and email metadata may be added. Website failure is recoverable at prospect level by approved direction; the error representation belongs to the future error-model phase.

## Runtime variability and debt

Live execution is externally variable. The baseline observed successful runs as well as navigation `TimeoutError` and selector `LookupError` in equivalent small runs. The pipeline also contains fixed waits, source-specific selectors, embedded browser lifecycle, diagnostic prints, heterogeneous exceptions and incomplete contact/about/content type metadata. These findings justify future stability work and should not be hidden or frozen as desired behavior.

## Target — TARGET_V0_7_X / TARGET_V1_0

The stabilization line aims to make this source pipeline a consumer of reusable runtime, configuration and error boundaries behind `ProspectorEngine`. It does not require formal page pagination or physical Engine extraction before `v1.0.0`.

## Relationship with the global architecture

Google Maps is the currently implemented source strategy inside the broader project. Its browser/feed/detail phases are source-specific. A future source could use traditional HTML, another browser-driven application, an API or another public interface and could therefore require a substantially different pipeline while still producing the shared domain/result boundary. `WebsiteEngine`, selector infrastructure, navigation boundaries and export infrastructure may be reused when their behavior applies; they are not mandatory steps for every future source.

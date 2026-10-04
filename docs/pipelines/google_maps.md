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

`NavigationEngine` is the access point used by the search stage. `GoogleMapsNavigation` receives a page factory from `BrowserRuntime`, opens Google Maps, enters the query and waits for the result view. It is source-specific; a generic multi-source navigation contract is not yet implemented.

## Result loading

Google Maps behaves as a single-page application with a virtual/infinite feed. The navigation path waits for an actionable input and for a visible feed with results; an absent feed or zero links is not treated as a verified empty search because no reliable empty marker has been established. The result-list path owns source-specific feed scrolling. It captures valid candidates before each scroll, tracks first-seen source hrefs in discovery order, and waits within finite attempt/time budgets for a new valid identity. Scroll movement, spinner activity and DOM count changes alone do not reset its stall detection. `LazyChargeEngine` supplies reusable semantic visibility waits, including delayed selector mounting; it does not own Maps scrolling.

`LazyChargeEngine` has a broader design scope than Google Maps alone: it provides semantic waiting, optional-selector handling and DOM-readiness coordination for dynamically rendered, lazy or virtual content. Google Maps is its current consumer because the Maps web application requires this kind of synchronization. Other sources may reuse it when their rendering strategy requires it, but no other source is currently implemented and not every future source would necessarily need it.

This is not formal page pagination. `limit` bounds Businesses processed/returned, while Google Maps may load a larger DOM batch. A run can therefore load six DOM results and return three Businesses for `limit=3` without violating the contract.

## Summary extraction

The first pass parses available name, category, address, phone and Maps href data into ordered `Business` objects. Invalid early cards do not consume the positive Business limit. Repeated source hrefs are skipped to avoid processing recycled cards, while distinct same-name Businesses remain separate. On a bounded feed stall, already valid Businesses are returned; if none exist and no verified terminal state exists, the search fails as indeterminate. The pipeline does not claim complete source coverage. The legacy `limit <= 0` path still navigates/resolves the feed and returns zero Businesses when that path succeeds. Known parser mojibake is technical debt, not a desired contract.

## Detail enrichment

The detail stage confirms the exact target click, checks a verifiable target place ID in navigation state, requires a fresh matching panel and compares names using only whitespace trimming/collapse and case-insensitive matching. A bounded reverse/forward feed search can recover an exact recycled href; failed recovery preserves the summary. Optional values equal to the prior panel's fields are not attributed to the new Business based on two stable reads alone. Recoverable skips are reported through `SearchResult.issues`. Concrete selectors, waits and URL assumptions remain source-specific implementation details.

The identity-first enrichment design exists to avoid associating a later panel state with the wrong result. The first pass retains stable information such as the extracted name and Maps href; subsequent phases validate the expected identity before mutating the same `Business` object. This is a design rationale, not a claim that all current synchronization is deterministic.

## Website enrichment

When a website is available, the scraper delegates inspection to Website Engine. Status/final URL, title, description, language and email metadata may be added. Website failure is recoverable at prospect level by approved direction; the error representation belongs to the future error-model phase.

## Runtime variability and debt

Live execution is externally variable. Controlled offline tests cover state, progress, identity, optional enrichment and runtime cleanup. In the single authorized C05 pilot, requests for 3 and 10 Businesses returned that many summaries, but all detail attempts remained unverified; a 25-Business request reached the hard 180-second process timeout and stopped the pilot. These outcomes do not establish a safe Engine maximum or a reliable empty-state marker. Browser lifecycle belongs to `BrowserRuntime`; Engine fatal boundaries use typed exceptions, while the legacy wrapper retains historical behavior.

## Target — TARGET_V0_7_X / TARGET_V1_0

The stabilization line aims to make this source pipeline a consumer of reusable runtime, configuration and error boundaries behind `ProspectorEngine`. It does not require formal page pagination or physical Engine extraction before `v1.0.0`.

## Relationship with the global architecture

Google Maps is the currently implemented source strategy inside the broader project. Its browser/feed/detail phases are source-specific. A future source could use traditional HTML, another browser-driven application, an API or another public interface and could therefore require a substantially different pipeline while still producing the shared domain/result boundary. `WebsiteEngine`, selector infrastructure, navigation boundaries and export infrastructure may be reused when their behavior applies; they are not mandatory steps for every future source.

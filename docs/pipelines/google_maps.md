# Google Maps Scraper Pipeline

## Purpose

This document describes the internal execution pipeline of the Google Maps scraper.

Unlike the global engine pipeline, this document focuses exclusively on how the Google Maps integration retrieves, validates and incrementally enriches business information.

The scraper is responsible only for interacting with Google Maps and producing normalized business entities for the engine.

The extraction process is organized as a deterministic multi-phase pipeline. Each phase has a single responsibility and must satisfy its own execution contract before transferring control to the next stage.

---

# Design Principles

The Google Maps scraper follows the same architectural principles as the rest of Prospector CLI:

* Single responsibility
* Modularity
* Performance
* Deterministic synchronization
* Identity-based enrichment
* Source independence

Its internal implementation may evolve without affecting the global execution pipeline.

---

# Pipeline Contracts

The scraper is organized around explicit contracts between phases.

Each phase guarantees a valid postcondition before the following phase begins.

```text
Navigation Engine
        │
        │ Guarantees:
        │ Google Maps is open and the search has been executed.
        ▼
LazyCharge Engine
        │
        │ Guarantees:
        │ Every available search result has been loaded.
        ▼
Identity Registration
        │
        │ Guarantees:
        │ Every Business has a stable identity.
        ▼
Detail Panel Enrichment
        │
        │ Guarantees:
        │ The opened detail panel belongs to the expected Business.
        ▼
Website Engine
        │
        │ Guarantees:
        │ Website metadata belongs to the validated Business.
        ▼
SearchResult
```

This contract-based design reduces synchronization issues between phases and keeps responsibilities clearly separated.

---

# Synchronization Strategy

Google Maps is a Single Page Application (SPA).

Selecting a business does not trigger a browser navigation.

Instead, JavaScript dynamically replaces the content of the existing detail panel.

For this reason, synchronization is based on application state transitions rather than browser navigation events.

The scraper follows one fundamental rule:

> Never synchronize using fixed delays.

Methods such as:

```python
page.wait_for_timeout(...)
```

or

```python
time.sleep(...)
```

must never be used.

Every interaction must wait only for the specific application state required by the following operation.

Synchronization is therefore deterministic, reproducible and independent of arbitrary timing assumptions.

---

# Performance Strategy

To reduce browser overhead while preserving extraction reliability, the scraper follows these optimization principles:

* Store immutable business identities instead of live DOM references.
* Store stable business identifiers instead of Playwright locators.
* Use JavaScript whenever browser interaction is unnecessary.
* Minimize browser round trips.
* Read multiple DOM values using a single browser evaluation.
* Synchronize through deterministic application state changes.
* Perform independent enrichment passes without repeating previous work.

These optimizations improve execution speed without increasing architectural complexity.

---

# Incremental Enrichment Strategy

Business extraction is intentionally divided into independent enrichment passes.

Each phase enriches the same Business entities while preserving every previously validated attribute.

The pipeline never restarts from the beginning after completing a successful phase.

This strategy provides several advantages:

* previously extracted information is preserved;
* failures remain isolated to the current phase;
* retry strategies can be implemented without repeating earlier work;
* every Business evolves incrementally until fully populated;
* the pipeline remains resilient without introducing unnecessary complexity.

---

# Business Identity

Business identity is established during the first extraction pass.

Each Business stores immutable information that allows subsequent phases to reliably identify the corresponding result.

The identity is composed of stable attributes collected from the result list, including:

* Internal extraction index
* Business name
* Google Maps href

Subsequent enrichment phases must validate this identity before updating the Business.

The scraper therefore operates on business identity rather than temporary DOM position.

This prevents asynchronous interface updates from associating extracted information with the wrong entity.

---

# Execution Phases

## Phase 1 — Navigation

Navigation is fully delegated to the Navigation Engine.

Its responsibility ends when Google Maps has executed the requested search and the result list is available.

Responsibilities:

* Open Google Maps.
* Resolve search UI selectors.
* Write the complete search query.
* Execute the search.
* Wait until the search results become available.

```text
SearchQuery

↓

Navigation Engine

↓

Google Maps

↓

Search Executed

↓

End Phase
```

---

## Phase 2 — Result Preparation

Result preparation is fully delegated to the LazyCharge Engine.

The scraper does not know how results are loaded.

Its only expectation is that the complete result set is ready before extraction begins.

Responsibilities:

* Wait for the result feed.
* Perform automatic scrolling.
* Synchronize dynamic loading.
* Detect loading completion.
* Guarantee that every available result has been loaded.

```text
Search Results

↓

LazyCharge Engine

↓

Wait Feed

↓

Automatic Scroll

↓

Synchronization

↓

Loading Complete

↓

End Phase
```

---

## Phase 3 — Identity Registration

The scraper performs the first extraction pass over the loaded result list.

Only summary information is collected during this phase.

No enrichment is performed.

Information extracted includes:

* Internal extraction index
* Business name
* Category
* Address (when available)
* Phone number (when available)
* Google Maps href

The collected information creates the initial Business collection.

```text
Loaded Results

↓

Read Summary

↓

Create Business

↓

Assign Internal Identity

↓

Store href

↓

Business[]

↓

End Phase
```

---

## Phase 4 — Detail Panel Enrichment

Each Business is processed independently.

Before enriching any information, the scraper validates that the currently opened detail panel belongs to the expected Business.

Only after successful validation is the Business updated.

Responsibilities:

1. Locate the business using its stored identity.
2. Open the corresponding detail panel.
3. Wait for the panel update.
4. Validate Business identity.
5. Read every required field using a single JavaScript evaluation.
6. Update the Business.

Typical information extracted includes:

* Full address
* Phone number
* Website

Future versions may enrich additional business attributes during this phase.

```text
Business

↓

Locate Business

↓

Open Detail Panel

↓

Wait Panel Update

↓

Validate Identity

↓

Read Complete Panel

↓

Update Business

↓

Next Business
```

If identity validation fails, the Business is not updated until the correct result has been located.

This guarantees deterministic enrichment and prevents cross-association between businesses.

---

## Phase 5 — Website Inspection

Once a Business has been validated and enriched with its Google Maps information, website inspection is delegated to the Website Engine.

The Google Maps scraper is responsible only for providing the validated website URL.

Website analysis remains completely reusable by future scraper implementations.

Typical workflow:

```text
Validated Business

↓

Website Available?

↓

Website Engine

↓

Extract Email

↓

Detect Language

↓

Collect Metadata

↓

Update Same Business

↓

Next Business
```

---

# Internal Pipeline

The complete Google Maps scraper workflow is summarized below.

```text
SearchQuery
        │
        ▼
Navigation Engine
        │
        ▼
Search Executed
        │
        ▼
LazyCharge Engine
        │
        ▼
All Results Loaded
        │
        ▼
Phase 1
Identity Registration
        │
        ▼
Business[]
        │
        ▼
Phase 2
Detail Panel Enrichment
        │
        ▼
Validated Business
        │
        ▼
Phase 3
Website Inspection
        │
        ▼
SearchResult
```

---

# Relationship with the Global Pipeline

This document describes only the internal behavior of the Google Maps scraper.

From the engine perspective, the scraper behaves as a single execution stage.

```text
SearchQuery

↓

Navigation Engine

↓

Google Maps Scraper

↓

Business[]

↓

Website Engine

↓

SearchResult

↓

Export Service
```

This separation allows every scraper to implement its own optimized extraction strategy while preserving a consistent architecture throughout the engine.

---

# Future Evolution

The Google Maps scraper is expected to evolve independently from the rest of the engine.

Future improvements may include:

* Adaptive synchronization strategies.
* Retry policies based on Business identity.
* Parallel website inspection.
* Multiple navigation profiles.
* Additional scraper implementations.
* Performance telemetry.
* Incremental checkpoint recovery.
* Enhanced DOM change detection.
* Source-specific Navigation Engine implementations.

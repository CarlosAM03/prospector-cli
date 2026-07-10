# Google Maps Scraper Pipeline

## Purpose

This document describes the internal execution pipeline of the Google Maps scraper.

Unlike the global engine pipeline, this document focuses exclusively on how the Google Maps integration retrieves and enriches business information.

The scraper is responsible only for interacting with Google Maps and producing normalized business entities for the engine.

---

# Design Principles

The Google Maps scraper follows the same architectural principles as the rest of Prospector CLI:

- Single responsibility
- Modularity
- Performance
- Deterministic synchronization
- Source independence

Its internal implementation may evolve without affecting the global execution pipeline.

---

# Synchronization Strategy

Google Maps is a Single Page Application (SPA).

Selecting a business does not perform a page navigation.

Instead, JavaScript updates the content of the existing detail panel.

For this reason, synchronization is performed by observing application state changes rather than browser navigation events.

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

should never be used.

Instead, every interaction should wait only for the specific state change required by the next operation.

This strategy minimizes execution time while improving extraction reliability.

---

# Performance Strategy

To reduce browser overhead, the scraper follows these optimization principles:

- Store immutable identifiers instead of live locators.
- Use JavaScript when browser interaction is unnecessary.
- Minimize browser round trips.
- Read multiple DOM values in a single browser evaluation.
- Synchronize using deterministic DOM changes.

These optimizations improve execution speed without increasing architectural complexity.

---

# Execution Phases

## Phase 1 — Result List Extraction

The scraper scans the search results and creates an initial collection of business entities.

Information extracted during this phase includes:

- Business name
- Category
- Address (when available)
- Phone number (when available)
- Google Maps href

The collected href is stored instead of the Playwright Locator.

This makes the collected data independent from future DOM changes.

```text
Search Results

↓

Business[]

↓

Store href

↓

End Phase
```

---

## Phase 2 — Detail Panel Enrichment

Each stored href is processed individually.

The scraper performs the following steps:

1. Locate the result using its href.
2. Trigger the click through JavaScript.
3. Wait until the business displayed in the detail panel changes.
4. Read every required field from the panel using a single JavaScript evaluation.
5. Update the Business model.

```text
Business

↓

Click using href

↓

Wait for business change

↓

Read complete panel

↓

Update Business
```

Typical information extracted during this phase:

- Address
- Phone number
- Website

Future versions may enrich additional business attributes here.

---

## Phase 3 — Website Inspection

If a business provides a website, the scraper delegates its inspection to a reusable website extraction module.

The Google Maps scraper is responsible only for providing the website URL.

Website analysis is intentionally separated so it can be reused by future scrapers.

Typical workflow:

```text
Business

↓

Website available?

↓

Open website

↓

Extract email

↓

Detect language

↓

Collect metadata

↓

Update Business
```

---

# Internal Pipeline

The complete Google Maps scraper workflow is summarized below.

```text
Phase 1
====================

Read result list

↓

Create Business[]

↓

Store href

↓

End


Phase 2
====================

For each Business

↓

Locate using href

↓

JavaScript click

↓

Wait for business change

↓

Read complete detail panel

↓

Update Business

↓

Next Business


Phase 3
====================

For each Business

↓

Website available?

↓

Open website

↓

Extract email

↓

Detect language

↓

Collect metadata

↓

Close page

↓

Next Business
```

---

# Relationship with the Global Pipeline

This document describes only the internal behavior of the Google Maps scraper.

From the engine perspective, the scraper behaves as a single pipeline stage.

```text
Query Builder

↓

Google Maps Scraper

↓

Business[]

↓

Normalization

↓

Validation

↓

Exporter
```

This separation allows every scraper to implement its own optimized extraction strategy while preserving a consistent architecture throughout the engine.

---

# Future Evolution

The Google Maps scraper is expected to evolve independently from the engine.

Potential improvements include:

- Automatic scrolling.
- Adaptive extraction strategies.
- Selector abstraction.
- Retry policies.
- Incremental enrichment.
- Parallel website inspection.
- Performance metrics.
- Selector Engine integration.
- DOM change detection improvements.
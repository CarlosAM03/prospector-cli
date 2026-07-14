# Roadmap

This roadmap describes the planned evolution of Prospector CLI.

The project follows an incremental development strategy focused on delivering a functional extraction engine as quickly as possible while preserving a modular architecture.

The first stable release (v1.0.0) represents the technical proof of concept for the engine and serves as the foundation for future integrations with external platforms.

---

# v0.1.0 — Project Bootstrap

**Status:** Completed

## Objectives

- [x] Establish the project structure.
- [x] Configure the Python development environment.
- [x] Integrate Playwright.
- [x] Implement Google Maps navigation.
- [x] Support interactive search queries.
- [x] Validate browser automation.

---

# v0.2.0 — Initial Data Extraction

**Status:** Completed

## Objectives

- [x] Extract business names.
- [x] Extract business categories.
- [x] Extract business addresses.
- [x] Extract business phone numbers.
- [x] Create internal business models.
- [x] Normalize raw extracted data into structured business entities.

---

# v0.3.0 — Business Detail Extraction

**Status:** Completed

## Objectives

- [x] Open the business detail panel.
- [x] Complete missing business information.
- [x] Improve address reliability.
- [x] Improve phone number reliability.
- [x] Extract business websites.
- [x] Handle missing information gracefully.
- [x] Replace locator-based navigation with href-based navigation.
- [x] Reduce unnecessary synchronization time.
- [x] Optimize panel extraction using a single JavaScript evaluation.

---

# v0.4.0 — Export Engine

**Status:** Completed

## Objectives

[x] Excel export.
[x] CSV export.
[x] Standardized output structure.
[x] Export pipeline.
[x] Output file naming strategy.

---

# v0.5.0 — Selector Infrastructure

Status: Completed

## Objectives

[x] Introduce Selector Engine.
[x] Introduce Elector Engine.
[x] Implement selector registry.
[x] Support semantic selector profiles.
[x] Decouple scraper logic from DOM selectors.
[x] Centralize selector resolution.
[x] Support selector fallback strategies.
[x] Prepare synchronization engine
---

# v0.6.0 — Website Inspection

**Status:** Planned

## Objectives

- Visit the business website.
- Find business email addresses.
- Detect the primary website language.
- Detect multilingual websites when possible.
- Validate website availability.
- Enrich business entities with website metadata.

---

# v0.7.0 — Search Automation

**Status:** Planned

## Objectives

- Automatic scrolling.
- Configurable extraction limits.
- Stable execution flow.
- Automatic pagination handling.
- Automatic lazy-loading support.

---

# v0.8.0 — Configuration Profiles

**Status:** Planned

## Objectives

- Configuration file support.
- Default execution profile.
- Custom user profiles.
- CLI profile selection.
- Interactive input fallback.

---

# v1.0.0 — MVP Release

## Goal

Deliver a complete command-line prospecting engine capable of producing structured business prospect lists from Google Maps.

### Functional Scope

- Interactive CLI.
- Configuration profiles.
- Google Maps scraper.
- Structured business extraction.
- Website inspection.
- Business normalization.
- Excel export.
- Configurable execution.
- Performance metrics.
- Extensible scraper architecture.

This release represents the first production-ready proof of concept for validating the engine before its integration into higher-level commercial platforms.

---

# Beyond v1.0.0

Future development will focus on extending the engine without changing its architectural principles.

Potential areas include:

- Additional public data sources.
- Additional export formats.
- Plugin-based scrapers.
- Improved normalization strategies.
- Parallel execution.
- Performance benchmarking.
- Distributed execution.

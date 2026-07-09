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

Status: Completed

## Objectives

- [x] Extract business names.
- [x] Extract business categories.
- [x] Extract business addresses.
- [x] Extract business phone numbers.
- [x] Create internal business models.
- [x] Normalize raw extracted data into structured business entities.

---

# v0.3.0 — Detail Extraction

## Objectives

- Open the business detail panel.
- Complete missing business information.
- Extract business website when available.
- Improve extraction reliability.
- Handle incomplete or unavailable information.

---

# v0.4.0 — Export Engine

## Objectives

- Excel export.
- CSV export.
- Standardized output structure.

---

# v0.5.0 — Search Automation

## Objectives

- Automatic result scrolling.
- Configurable extraction limits.
- Automatic detail extraction.
- Stable execution flow.

---

# v0.6.0 — Configuration Profiles

## Objectives

- Configuration file support.
- Default execution profile.
- Custom user profiles.
- Profile selection from the CLI.
- Interactive input fallback.

---

# v1.0.0 — MVP Release

## Goal

Deliver a complete command-line prospecting engine capable of producing structured business prospect lists from Google Maps.

### Functional Scope

- Interactive CLI.
- Configuration profiles.
- Google Maps scraper.
- Business data extraction.
- Business normalization.
- Excel export.
- Configurable search execution.

This release serves as the first production-ready proof of concept for validating the engine before its integration into higher-level commercial platforms.

---

# Beyond v1.0.0

Future development will focus on extending the engine without changing its architectural principles.

Potential areas include:

- Additional public data sources.
- Additional export formats.
- Improved normalization strategies.
- Performance optimizations.

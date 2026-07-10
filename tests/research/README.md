# Research Scripts

This directory contains exploratory scripts created to understand the behavior of supported public sources.

These scripts are intentionally isolated from the production code.

## Google Maps DOM Lifecycle

Purpose

- Verify whether Google Maps replaces or reuses the detail panel.
- Inspect URL changes after selecting a business.
- Validate synchronization strategies.
- Evaluate Playwright interaction methods.

Key findings

- Google Maps behaves as a Single Page Application.
- The detail panel persists between businesses.
- Only the panel content changes.
- Synchronization by state change is faster than waiting for navigation.
- JavaScript click is sufficient for opening businesses.
- Business information can be extracted in a single JavaScript evaluation.

Impact

These findings led to the Phase 2 redesign implemented in v0.3.0.
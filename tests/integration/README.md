# Integration Tests

This directory validates interactions between existing components in controlled environments.

Current tests use controlled localhost Website Engine fixtures, mocked source/global pipeline behavior and temporary paths for `ExportService` CSV/XLSX output. They do not access Google Maps or the public Internet; no Playwright-managed browser install is required for the ordinary suite. Live Google Maps behavior belongs in `tests/e2e/` and is opt-in.

Assertions should protect observable contracts such as parsed metadata, result flow and export schema, not browser waits, concrete selectors or other known source-specific debt.

The category is intentionally broad enough for controlled Website Engine execution, export integration and future controlled scraper-pipeline checks. A real Google Maps run remains an external E2E concern rather than a deterministic integration prerequisite.

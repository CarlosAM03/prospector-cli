# Prospector CLI

Prospector CLI is an independent open-source Python CLI for extracting structured business information from public sources. The current implementation is CLI-first and centered on a Google Maps pipeline.

The project is not a SaaS, web API, CRM, ERP, DATRA backend or distributed platform. Other applications may consume its results, but those applications are outside this repository.

## Current behavior

```text
CLI input
  -> SearchQuery
  -> Google Maps navigation and virtual/infinite feed loading
  -> summary extraction into Business objects
  -> detail-panel enrichment
  -> optional Website Engine enrichment
  -> SearchResult
  -> CSV or XLSX export through ExportService
```

The current programmatic boundary is:

```python
search_businesses(query: SearchQuery, limit: int = 50) -> SearchResult
```

This is transitional, not the approved stable `v1.0.0` Engine contract. The interactive CLI currently invokes the pipeline with `limit=500`. That limit bounds Businesses processed/returned; it does not guarantee that Google Maps loads no additional DOM nodes.

Businesses may remain partially enriched when detail-panel or website inspection cannot provide every field. Website inspection currently covers basic status/final URL, title, description, language and email extraction. Contact/about detection and effective `content_type` output remain incomplete.

## Project purpose and design principles

The project is intended to turn public-source information into reusable structured prospect data while keeping business workflows outside the repository. Its architectural direction is based on small responsibilities, source-specific pipelines, incremental enrichment, reusable infrastructure and clear boundaries between extraction, results and export.

Some of that direction is already represented by current modules; some is the target toward `v1.0.0`. Formal normalization, validation, deduplication and configuration profiles must not be inferred from this design description as currently implemented.

## Installation

Create and activate a virtual environment using a Python version available in your environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m playwright install chromium
```

The audit/regression checkpoint observed compatibility with Python 3.13.4, pytest 9.1.1 and Playwright 1.61.0/Chromium. This observation does not define the project's official Python compatibility policy.

## Run the CLI

```powershell
python src/main.py
```

The CLI asks for keyword and location, runs the current Google Maps pipeline and offers CSV/XLSX export. It opens a visible Chromium browser under the current implementation.

## Exports

`ExportService` consumes `SearchResult` directly and is reusable application/export infrastructure. It is outside the extraction core and is not CLI-only. Current CSV/XLSX columns are:

```text
Name, Category, Address, Phone, Email, Website, Language
```

## Tests

Install development dependencies separately:

```powershell
python -m pip install -r requirements-dev.txt
```

Run the deterministic and controlled regression baseline:

```powershell
python -m compileall -q src
python -m pytest --collect-only -q
python -m pytest tests\unit -q
python -m pytest tests\integration -q
python -m pytest -q
```

The default suite does not require Internet and does not reach Google Maps. The Website Engine integration test uses localhost and local Chromium. The live Google Maps check is opt-in:

```powershell
$env:PROSPECTOR_RUN_E2E = "1"
python -m pytest -m e2e -q
Remove-Item Env:PROSPECTOR_RUN_E2E
```

See `tests/README.md` and `docs/contributing.md` for the test policy and contributor checks.

## Architecture direction

The current scraper owns Playwright/browser lifecycle and source-specific extraction. Internal diagnostics still include `print` calls and error handling is heterogeneous.

The approved target is:

```text
CLI adapter -> ProspectorEngine(config) -> extraction pipeline -> SearchResult
                                                        |
                                                        +-> ExportService -> CSV/XLSX
```

`ProspectorEngine` and `EngineConfig` do not exist yet. Formal normalization, structured errors/issues, multi-input, deduplication and merge are future work. Physical extraction into a separately packaged Engine is a post-v1 possibility, not a prerequisite for `v1.0.0`.

## Project evolution

The current stabilization line builds on earlier work rather than restarting the project. Historical milestones include initial Google Maps navigation and summary extraction, detail-panel enrichment, standardized `SearchResult`/export output, selector infrastructure, Website Engine enrichment, Navigation Engine integration and lazy/dynamic-content synchronization support. These milestones explain why the repository contains reusable engines and source-specific modules; they do not mean every planned abstraction is complete today.

The public route is now:

```text
previous extraction and reusable-components work
        -> v0.7.x stability and decoupling
        -> v0.8.x normalization
        -> v0.9.x multi-input and deduplication
        -> v1.0.0 stable extraction-ready release
        -> post-v1 packaging/consumer possibilities
```

## Scope

This repository focuses on obtaining structured prospect data from public sources. It does not implement CRM/ERP, customer or user management, marketing automation, sales workflows, dashboards, analytics, persistence, jobs or distributed execution.

## Contributing and license

Read `docs/contributing.md` before contributing. The project license is in `LICENSE`.

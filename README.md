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

This wrapper remains transitional and preserves its default of 50, including the legacy nonpositive-limit behavior and requests above 100. The CLI calls `ProspectorEngine` with an optional limit: Enter selects 50, and valid requests are 1 through 100. The owner approved 100 as the Google Maps Engine maximum; larger or invalid requests are rejected before Chromium starts, without clamping. This operational policy is not a statistical guarantee of capacity.

Businesses may remain partially enriched when detail-panel or website inspection cannot provide every field. Website inspection currently covers basic status/final URL, title, description, language and email extraction. Contact/about detection and effective `content_type` output remain incomplete.

## Philosophy

Prospector CLI turns public-source information into reusable structured prospect data while keeping CRM, sales and other business workflows outside the repository. The project favors a lightweight, readable and modular extraction system that can evolve without becoming a private application platform.

## Design Principles

The project is guided by:

- single responsibility and simplicity;
- modular, readable components;
- reusable extraction infrastructure;
- source-specific extraction pipelines;
- incremental enrichment of domain objects;
- clear separation between extraction, presentation and export;
- extensibility for future source strategies;
- configuration over hardcoded execution behavior as the architecture evolves.

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

The CLI asks for keyword, location and an optional limit (default 50, maximum 100). It presents recoverable issues and offers CSV/XLSX export after a successful search. The programmatic `search_businesses` wrapper remains available with its legacy behavior.

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

`BrowserRuntime` owns Playwright/browser lifecycle for each search. The Google Maps pipeline owns source-specific extraction, while reusable components use module logging for diagnostics. `SearchResult.issues` and fatal `ProspectorError` categories provide the approved Error Model. A bounded feed stall preserves valid Businesses and records an issue; a verifiable source end would return available Businesses without a stall issue. No reliable live empty/end marker has been established.

The approved target is:

```text
CLI adapter -> ProspectorEngine(config) -> extraction pipeline -> SearchResult
                                                        |
                                                        +-> ExportService -> CSV/XLSX
```

`EngineConfig` and `ProspectorEngine` are integrated with the CLI under the owner-approved Google Maps maximum of 100. The wrapper remains the legacy programmatic path. Offline tests cover the feed/detail/website flow. The owner completed two manual CLI searches and CSV/XLSX exports at limits 75 and 50; these demonstrate operation for those queries, not catalog completeness or universal reliability. Formal normalization, multi-input, deduplication and merge remain future work. Physical extraction into a separately packaged Engine is a post-v1 possibility, not a prerequisite for `v1.0.0`.

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

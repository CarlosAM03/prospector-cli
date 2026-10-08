# Prospector CLI

Prospector CLI is an independent open-source Python CLI for extracting structured business information from public sources. The current implementation is CLI-first and centered on a Google Maps pipeline.

The project is not a SaaS, web API, CRM, ERP, DATRA backend or distributed platform. Other applications may consume its results, but those applications are outside this repository.

The v1.0.0 source and Windows portable release candidate are implemented and verified offline. Final owner acceptance (R20) is pending; no stable release, tag or public ZIP has been published.

## Current behavior

```text
CLI input
  -> SearchQuery
  -> Google Maps navigation and virtual/infinite feed loading
  -> summary extraction into Business objects
  -> detail-panel enrichment
  -> optional Website Engine enrichment
  -> consolidated original Business[]
  -> mandatory global normalization
  -> SearchResult with NormalizedBusiness[] and original Business[]
  -> CSV or XLSX export through ExportService
```

The current programmatic boundary is:

```python
search_businesses(query: SearchQuery, limit: int = 50) -> SearchResult
```

This wrapper remains transitional and preserves its default of 50, including the legacy nonpositive-limit behavior and requests above 100. The CLI calls `ProspectorEngine` with an optional limit: Enter selects 50, and valid requests are 1 through 100. The owner approved 100 as the Google Maps Engine maximum; larger or invalid requests are rejected before browser startup, without clamping. This operational policy is not a statistical guarantee of capacity.

Both supported single-search entrypoints normalize after source enrichment. `result.businesses` contains independent `NormalizedBusiness` objects; `result.original_businesses` retains the consolidated `Business` objects in matching order. `result.total_found` counts extracted businesses, and `result.issues` includes source and recoverable normalization issues. The CLI displays and exports the normalized view. Normalization is local and deterministic.

Businesses may remain partially enriched when detail-panel or website inspection cannot provide every field. Website inspection currently covers basic status/final URL, title, description, language and email extraction. Contact/about detection and effective `content_type` output remain incomplete.

The accepted v0.9.x implementation baseline `c7193d55a36618e934e29a9678b3f9b01e9b6543` also provides `ProspectorEngine.search_many()` for 1–5 ordered `BatchQuery` requests and a CLI `Multiple Searches` path for 2–3 requests. Each query has its own limit and browser lifecycle. `BatchSearchResult.entries` retain complete individual results, safe failures, counts and per-observation provenance. A verified, namespaced Google Place ID can suppress an observation only in a *later* query; `UNVERIFIED` identity and repetitions within one query remain exportable. Batch CSV/XLSX files are separate per valid query, including a header-only file when all rows were suppressed. The owner accepted P91–P96, the offline regression and two subsequent full CLI batches as G23 live evidence. v0.9.x is **OWNER ACCEPTED / COMPLETE**, not tagged or released. Apparent commercial duplicates may remain when identity is `UNVERIFIED`; this is an accepted limitation, not a reason to apply text matching.

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

The current modules implement the v1.0.0 CLI release-candidate scope. General validation, heuristic matching, persistence and configuration profiles are not included.

## Installation

Create and activate a virtual environment using a Python version available in your environment:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
# Microsoft Edge Stable must already be installed on Windows.
```

If `venv/` already exists, activate it and rerun the requirements install after pulling dependency changes. For source execution from VS Code, select `venv\Scripts\python.exe` as the interpreter and confirm it with `python -c "import sys; print(sys.executable)"`. PyInstaller is a build-only dependency in `requirements-build.txt`, not needed for source use.

The v1.0.0 runtime uses installed Microsoft Edge Stable via Playwright 1.61.0 `channel="msedge"` in both source and Windows portable execution. The portable includes Python and application dependencies but no browser executable; users do not need Python, a repository checkout, or `playwright install`. Edge Stable is an external prerequisite. Edge enterprise policies, mandatory extensions, proxies or organizational controls may interfere with automation. The earlier Chromium audit/regression checkpoint is historical, not the v1.0.0 runtime policy.

The CLI defaults to Visible mode; Background remains available. The candidate was validated on the primary Windows development host, including relocated portable execution. Separate clean-machine validation was deferred by explicit owner decision to post-release compatibility testing; environment-specific Windows or Edge issues may still be found. See [Windows portable guidance](docs/portable-windows.md).

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

The default suite does not require Internet and does not reach Google Maps. Controlled browser integration uses localhost; the live Google Maps check is opt-in:

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
CLI adapter -> ProspectorEngine(config) -> extraction -> normalization -> SearchResult
                                                                     | normalized + original
                                                                     +-> ExportService -> CSV/XLSX
```

`EngineConfig` and `ProspectorEngine` are integrated with the CLI under the owner-approved Google Maps maximum of 100. The wrapper remains the legacy programmatic path with the same mandatory normalization stage. Offline tests cover the feed/detail/website flow, both normalized result routes and the v0.9.x bounded batch path. The earlier two single-search manual exports at limits 75 and 50 belonged to the v0.7.x baseline; the owner's two later three-query CLI batches supplied v0.9.x G23 evidence. Those observations do not prove catalog completeness or universal reliability. Batch execution and exact interquery selection are CURRENT; field merge, heuristic matching and persistence remain outside the v1.0.0 candidate. Final hardening and portable packaging are implemented; owner acceptance and release publication remain pending. Physical extraction into a separately packaged Engine is a post-v1 possibility.

## Project evolution

The current stabilization line builds on earlier work rather than restarting the project. Historical milestones include initial Google Maps navigation and summary extraction, detail-panel enrichment, standardized `SearchResult`/export output, selector infrastructure, Website Engine enrichment, Navigation Engine integration and lazy/dynamic-content synchronization support. These milestones explain why the repository contains reusable engines and source-specific modules; they do not mean every planned abstraction is complete today.

The public route is now:

```text
previous extraction and reusable-components work
        -> v0.7.x stability and decoupling
        -> v0.8.x normalization
        -> v0.9.x multi-input and deduplication
        -> v1.0.0 release candidate (owner acceptance pending)
        -> post-v1 packaging/consumer possibilities
```

## Scope

This repository focuses on obtaining structured prospect data from public sources. It does not implement CRM/ERP, customer or user management, marketing automation, sales workflows, dashboards, analytics, persistence, jobs or distributed execution.

## Contributing and license

Read `docs/contributing.md` before contributing. The project license is in `LICENSE`.

# Contributing

Prospector CLI is an independent open-source CLI project. Contributions should preserve current user-facing behavior unless a change explicitly belongs to an approved future phase.

## State vocabulary

Use these distinctions when reviewing a change:

- `CURRENT`: implemented behavior;
- `TECHNICAL_DEBT`: known implementation detail that should not become a desired contract;
- `TARGET_V0_8`, `TARGET_V0_9`, `TARGET_V1_0`: scope not yet implemented in an older checkpoint (check CURRENT first);
- `DEFERRED_DESIGN`: approved problem whose exact technical contract is not selected yet.

`EngineConfig`, `ProspectorEngine` and the approved public Error Model are present under the accepted v0.7.x technical baseline at `ee6b69e`. The owner-approved Google Maps Engine maximum is 100 and the CLI default is 50; changes to that policy need explicit approval. v0.8.x mandatory normalization and two public result views are owner accepted, with the historical N31 paired-live-inspection caveat. v0.9.x bounded sequential batch execution and exact verified-identity interquery selection are owner accepted on baseline `c7193d55a36618e934e29a9678b3f9b01e9b6543`; two later full CLI runs satisfied G23. `UNVERIFIED` observations remain exportable, even if they look commercially alike. Field merge, heuristic matching and historical/campaign deduplication remain outside current scope. v1.0.0 is the current stable released baseline; see the [release closure](releases/v1.0.0/RELEASED.md) and [freeze record](releases/v1.0.0/FREEZE.md). See [tracked history](history/README.md) for historical decisions.

## Project Philosophy

Contributions should help keep Prospector CLI independent, readable, modular and useful as an open-source extraction project. Code, documentation, bug reports, tests and design discussion are all valuable contributions. Favor small focused components, reusable infrastructure where it genuinely applies and source-specific pipelines where the target source requires specialized behavior.

The project favors small focused components, composition over large classes, readable code, reusable modules and source-specific extraction logic. Document non-obvious decisions, especially when a component has a reusable design scope but only one current consumer.

## Repository areas

```text
src/models/                 domain models
src/engines/                navigation, selector, website and normalization components
src/scraper/google_maps/    source-specific extraction pipeline
src/exporters/              output writers
src/services/               reusable services such as ExportService
src/utils/                  helpers
src/main.py                 current interactive CLI

tests/unit/                 deterministic tests
tests/integration/          controlled localhost/export tests
tests/e2e/                  opt-in external checks
tests/research/             exploratory tooling
tests/performance/          benchmark area
```

`ExportService` consumes `SearchResult` and is reusable export infrastructure, not CLI-only and not part of extraction core.

## Validation

Use the project's `venv\Scripts\python.exe` interpreter (or activate `venv\Scripts\Activate.ps1`) for source development. If an existing venv predates the current requirements, rerun both installs before testing; `Rich` is a runtime dependency, while PyInstaller is build-only.

```powershell
.\venv\Scripts\python.exe -m pip install -r requirements.txt
.\venv\Scripts\python.exe -m pip install -r requirements-dev.txt
# Microsoft Edge Stable is the v1.0.0 browser prerequisite; no Playwright browser install.

Remove-Item Env:PROSPECTOR_RUN_E2E -ErrorAction SilentlyContinue
$base = Join-Path $env:TEMP ("prospector-v100-freeze-" + [guid]::NewGuid().ToString("N"))
.\venv\Scripts\python.exe -m compileall -q src
.\venv\Scripts\python.exe -m pytest tests\unit -q -m "not e2e" --basetemp="${base}-unit"
.\venv\Scripts\python.exe -m pytest tests\integration -q -m "not e2e" --basetemp="${base}-integration"
.\venv\Scripts\python.exe -m pytest -q -m "not e2e" --basetemp="${base}-all"
git diff --check
```

The default suite must not require Internet or reach Google Maps. The controlled Website Engine test uses localhost. Production BrowserRuntime uses installed Microsoft Edge Stable through Playwright `channel="msedge"` for both modes.

The live external check is opt-in:

```powershell
$env:PROSPECTOR_RUN_E2E = "1"
.\venv\Scripts\python.exe -m pytest -m e2e -q
Remove-Item Env:PROSPECTOR_RUN_E2E
```

Its result is evaluated separately because Google Maps can vary by network, DOM and navigation timing.

## Portable rebuild

On Windows x64, install `requirements.txt`, `requirements-dev.txt` and the build-only `requirements-build.txt` into the chosen build environment, then run `python scripts/build_windows_portable.py` with that environment's Python. The PyInstaller script writes an ignored `temp/b-*` onedir, copies notices/licenses and refuses a bundled browser executable. It does not create a GitHub Release or reproduce an accepted ZIP hash automatically. Installed Microsoft Edge Stable is a runtime prerequisite, not a redistributed component. Inspect the build and create/upload a ZIP only through a separately authorized release workflow; see [portable usage](portable-windows.md).

## Guidelines

- Keep changes focused and protect intentional contracts with semantic tests.
- Do not freeze fixed waits, selectors, print output, timestamps or other known debt.
- Keep source-specific behavior in the source pipeline.
- Keep CLI presentation separate from reusable extraction and export services.
- Do not introduce private consumer/product context into public documentation.
- Include Python version, OS, command, expected behavior and observed behavior when reporting failures.

## Git workflow

Use a branch for implementation work and a focused commit for each coherent change. Before a checkpoint, inspect `git status --short`, `git diff --check` and staged/unstaged file lists. Do not stage or commit unrelated files.

## Pull requests and issue reports

Keep pull requests focused on one purpose, explain the observable behavior affected and update the relevant owning documentation when a contract or phase boundary changes. For bugs, include Python version, operating system, command, reproduction steps, expected behavior, actual behavior and relevant logs or screenshots. External Google Maps failures should include enough context to distinguish network/DOM variability from deterministic regressions.

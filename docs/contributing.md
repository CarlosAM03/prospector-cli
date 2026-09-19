# Contributing

Prospector CLI is an independent open-source CLI project. Contributions should preserve current user-facing behavior unless a change explicitly belongs to an approved future phase.

## State vocabulary

Use these distinctions when reviewing a change:

- `CURRENT`: implemented behavior;
- `TECHNICAL_DEBT`: known implementation detail that should not become a desired contract;
- `TARGET_V0_7_X`, `TARGET_V0_8`, `TARGET_V0_9`, `TARGET_V1_0`: future scope;
- `DEFERRED_DESIGN`: approved problem whose exact technical contract is not selected yet.

Do not implement `ProspectorEngine`, `EngineConfig`, normalization, deduplication or structured errors merely because they appear in target documentation.

## Project Philosophy

Contributions should help keep Prospector CLI independent, readable, modular and useful as an open-source extraction project. Code, documentation, bug reports, tests and design discussion are all valuable contributions. Favor small focused components, reusable infrastructure where it genuinely applies and source-specific pipelines where the target source requires specialized behavior.

The project favors small focused components, composition over large classes, readable code, reusable modules and source-specific extraction logic. Document non-obvious decisions, especially when a component has a reusable design scope but only one current consumer.

## Repository areas

```text
src/models/                 domain models
src/engines/                navigation, selector and website components
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

```powershell
python -m pip install -r requirements.txt
python -m pip install -r requirements-dev.txt
python -m playwright install chromium

python -m compileall -q src
python -m pytest --collect-only -q
python -m pytest tests\unit -q
python -m pytest tests\integration -q
python -m pytest -q
```

The default suite must not require Internet or reach Google Maps. The controlled Website Engine test uses localhost and local Chromium.

The live external check is opt-in:

```powershell
$env:PROSPECTOR_RUN_E2E = "1"
python -m pytest -m e2e -q
Remove-Item Env:PROSPECTOR_RUN_E2E
```

Its result is evaluated separately because Google Maps can vary by network, DOM and navigation timing.

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

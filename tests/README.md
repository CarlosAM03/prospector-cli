# Tests

The test tree separates deterministic regression safety, controlled integration and externally variable live checks. Tests protect intentional contracts, not every current implementation detail.

## Structure

```text
tests/
├── unit/          deterministic contract tests
├── integration/   controlled localhost and export integration tests
├── e2e/           opt-in live external checks
├── research/      exploratory/manual tooling
└── performance/   reserved benchmark work
```

`tests/unit/` covers deterministic models, normalization rules and engine, helpers, website components, selector registry/fallback behavior and explicitly named characterization cases. `tests/integration/` covers the shared normalization path, CLI/export values, controlled localhost browser use and temporary export paths. These categories do not access Google Maps or the public Internet.

The offline suite additionally covers batch preflight/snapshot, identity-sidecar alignment and negative cases, sequential runtime/failure isolation, exact interquery selection, provenance, CLI confirmation and independent CSV/XLSX files. v1.0.0 adds durable BrowserRuntime/driver-isolation, controlled cancellation, CLI semantics, metrics, version and portable-export tests. Synthetic IDs validate algorithm behavior. The owner separately accepted two real v0.9.x CLI batches as G23; the narrow P92 identity study is preserved in [tracked history](../docs/history/v0.9.0/P92IdentityEvidence.md). Temporary R09/R10/R19 manual probes were diagnostic, not required regression inputs; their conclusions are preserved in [v1.0.0 history](../docs/history/v1.0.0/).

`tests/e2e/` contains live external checks. Enable the Google Maps check explicitly:

```powershell
$env:PROSPECTOR_RUN_E2E = "1"
.\venv\Scripts\python.exe -m pytest -m e2e -q
Remove-Item Env:PROSPECTOR_RUN_E2E
```

Do not assert fixed business names. Validate high-level invariants only. Live failures are evaluated separately from deterministic regressions.

Research scripts are exploratory/manual tooling, not permanent pytest contracts. Performance tests are reserved for later benchmark work.

## Environment and commands

Development dependencies are separate from runtime dependencies:

```powershell
.\venv\Scripts\python.exe -m pip install -r requirements-dev.txt
```

The historical Phase 1 checkpoint used Python 3.13.4 and pytest 9.1.1. v1.0.0 production browser policy is installed Microsoft Edge Stable through Playwright 1.61.0 `msedge`; historical Chromium observations do not supersede it. The project `venv` is the source regression environment.

```powershell
Remove-Item Env:PROSPECTOR_RUN_E2E -ErrorAction SilentlyContinue
$base = Join-Path $env:TEMP ("prospector-v100-freeze-" + [guid]::NewGuid().ToString("N"))
.\venv\Scripts\python.exe -m compileall -q src
.\venv\Scripts\python.exe -m pytest tests\unit -q -m "not e2e" --basetemp="${base}-unit"
.\venv\Scripts\python.exe -m pytest tests\integration -q -m "not e2e" --basetemp="${base}-integration"
.\venv\Scripts\python.exe -m pytest -q -m "not e2e" --basetemp="${base}-all"
```

Use a fresh external `%TEMP%` basetemp, not a fixed repository-local `temp/audit_runtime` path; the latter has produced Windows permission/path failures. The exact count may grow. The invariant is that the default command remains green, offline-capable and excludes live external E2E.

## Regression policy

Before adding a test, classify the behavior as an intentional contract, a characterization, known debt that must not be frozen, or future-phase functionality. Prefer semantic assertions over snapshots and implementation details.

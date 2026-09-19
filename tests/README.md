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

`tests/unit/` covers deterministic models, helpers, website components, selector registry/fallback behavior and explicitly named characterization cases. `tests/integration/` uses localhost and temporary export paths. These categories do not access Google Maps or the public Internet.

`tests/e2e/` contains live external checks. Enable the Google Maps check explicitly:

```powershell
$env:PROSPECTOR_RUN_E2E = "1"
python -m pytest -m e2e -q
Remove-Item Env:PROSPECTOR_RUN_E2E
```

Do not assert fixed business names. Validate high-level invariants only. Live failures are evaluated separately from deterministic regressions.

Research scripts are exploratory/manual tooling, not permanent pytest contracts. Performance tests are reserved for later benchmark work.

## Environment and commands

Development dependencies are separate from runtime dependencies:

```powershell
python -m pip install -r requirements-dev.txt
```

The recorded Phase 1 checkpoint used Python 3.13.4, pytest 9.1.1 and Playwright 1.61.0/Chromium. These are observed validation versions, not an official Python support policy.

```powershell
python -m compileall -q src
python -m pytest --collect-only -q
python -m pytest tests\unit -q
python -m pytest tests\integration -q
python -m pytest -q
```

The exact test count may grow. The invariant is that the default command remains green, offline-capable and excludes live external E2E.

## Regression policy

Before adding a test, classify the behavior as an intentional contract, a characterization, known debt that must not be frozen, or future-phase functionality. Prefer semantic assertions over snapshots and implementation details.

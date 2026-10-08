# End-to-End Tests

This directory contains complete external-flow validations and is not assumed deterministic.

The live Google Maps smoke test is opt-in:

```powershell
$env:PROSPECTOR_RUN_E2E = "1"
.\venv\Scripts\python.exe -m pytest -m e2e -q
Remove-Item Env:PROSPECTOR_RUN_E2E
```

The documented offline release suite uses the project `venv`, `-m "not e2e"` and a unique external `%TEMP%` basetemp (see [`tests/README.md`](../README.md)); it does not require Internet or reach Google Maps. When this opt-in live test is enabled, assert only high-level invariants such as result type, query preservation, limit bounds and non-empty returned names; do not freeze external business names.

The category also provides a place for complete CLI/user-flow checks when they become safe to run explicitly. It is not a promise that a full interactive CLI E2E currently runs in the default suite.

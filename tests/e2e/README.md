# End-to-End Tests

This directory contains complete external-flow validations and is not assumed deterministic.

The live Google Maps smoke test is opt-in:

```powershell
$env:PROSPECTOR_RUN_E2E = "1"
python -m pytest -m e2e -q
Remove-Item Env:PROSPECTOR_RUN_E2E
```

The default `python -m pytest -q` suite does not require Internet and does not reach Google Maps. When enabled, assert only high-level invariants such as result type, query preservation, limit bounds and non-empty returned names; do not freeze external business names.

The category also provides a place for complete CLI/user-flow checks when they become safe to run explicitly. It is not a promise that a full interactive CLI E2E currently runs in the default suite.

# v0.7.x closure validation matrix

Baseline commit: `e266e74d8c2942a2f0c46cc00eef29b44c352eb1` (`main`, clean at start). The default suite remains deterministic/offline; the live smoke test remains opt-in.

| Gate | Command/evidence | Result |
| --- | --- | --- |
| Baseline | `.venv-audit/Scripts/python.exe -m pytest -q --basetemp=temp/audit_runtime/pytest-closure-baseline` | 95 passed, 1 deselected |
| H-01–H-04 focused | detail, feed, navigation, selector, virtual-feed and budget tests | 40 passed |
| H-01–H-04 full | `pytest -q --basetemp=temp/audit_runtime/pytest-closure-stage1` | 101 passed, 1 deselected |
| C01–C03 focused | SearchIssue, models, feed, facade, pipeline and typed errors | 41 passed |
| C01–C03 full | `pytest -q --basetemp=temp/audit_runtime/pytest-closure-stage2` | 109 passed, 1 deselected |
| CLI focused | migrated CLI, facade and export compatibility | 13 passed |
| Engine/CLI full | `pytest -q --basetemp=temp/audit_runtime/pytest-closure-stage4` | 115 passed, 1 deselected |
| Final unit | `pytest -q tests/unit --basetemp=temp/audit_runtime/pytest-closure-unit-final` | 92 passed |
| Final integration | `pytest -q tests/integration --basetemp=temp/audit_runtime/pytest-closure-integration-final` | 23 passed |
| Final full regression | `pytest -q --basetemp=temp/audit_runtime/pytest-closure-full-final` | 115 passed, 1 deselected |
| Source compilation | `.venv-audit/Scripts/python.exe -m compileall -q src` | passed at each stage |
| Diff whitespace | `git diff --check` | exit 0 at each stage; only LF/CRLF advisories |
| Live C05 | exact authorized pilot | 3 attempts; 2 returned, 1 hard timeout; 5 not started |

Coverage includes H-01 stale optional fields, H-02 recycled exact candidate and failed recovery, H-03 hidden/visible siblings, H-04 finite attribute waits; C01–C03 legacy SearchResult construction, independent issues, issue ordering/safety, detail/website/feed recovery, typed navigation/extraction/runtime errors, chaining and unexpected-error passthrough; C06/C07 CLI default/explicit/invalid limits, issue presentation, policy block, wrapper compatibility and export schema. No tests were weakened or skipped to pass these gates.

Live observations are separate from offline regression. They do not establish an approved `engine_max_limit` or release readiness.

## Final regression recovery on review/v0.7x-integration — 2026-10-04

Initial HEAD `545329ed9d219987c12d368d2f4950704586506c`, clean. Before edits, the offline suite returned **114 passed, 1 failed, 1 deselected**: the CLI used 100 when Enter was pressed, contrary to the approved default 50. The owner has now approved an operational Google Maps maximum of 100; this is policy, not a statistical capacity claim.

| Gate | Result |
| --- | --- |
| Compile source | passed |
| Unit suite | 110 passed |
| Integration suite | 27 passed |
| Complete default suite | 137 passed, 1 deselected |
| CLI launch without search | started and exited through menu option 2 |
| Diff whitespace | `git diff --check` exit 0, LF/CRLF advisories only |
| Live Google Maps | not executed; manual acceptance pending |

Controlled coverage added: requested limits 1/50/100/101 and invalid input; 100 and 105 distinct feed candidates; verified end seam versus bounded stall; transformed URL tokens; matching visible panel with repeated names; late panel, failed click, optional field freshness, recycled link recovery; and the detail-to-website-to-email path. The prior C05 observations remain historical evidence and were not repeated.

## Documentation closure verification — 2026-10-05

Verified at `ee6b69e90972fce62fb5f9cedcee23acbd3c6b15` without live access:

| Gate | Result |
|---|---|
| `python -m compileall -q src` | passed |
| Unit suite | 113 passed |
| Integration suite | 28 passed |
| Complete suite | 141 passed, 1 live E2E deselected |
| Live execution in this audit | none |

Owner-supplied smoke evidence is recorded separately from this offline run: Maquila/Tijuana limit 75 completed with CSV export; hospitales/Tijuana default 50 completed with XLSX export. Those runs demonstrate their observed flows and do not prove universal Maps completeness or field accuracy.

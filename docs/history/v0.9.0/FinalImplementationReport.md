# Prospector CLI v0.9.x — P96 Implementation Snapshot and v0.9.7 Closure

**Current status: `v0.9.x — OWNER ACCEPTED / COMPLETE`.** Implementation baseline `c7193d55a36618e934e29a9678b3f9b01e9b6543`; no tag or release. The original P96 report below is retained as a historical offline snapshot: its then-pending G23 and owner-action wording is superseded by the v0.9.7 closure at the end and `V0-9-0-Owner-Acceptance-Closure.md`.

## Repository and authorities

Branch `v0.9.0`; starting and final HEAD `d1880e7ca305ff326eeac9e1e7c1ccd02e981b1d`. Git worktree initially clean, now contains only the audited local changes in `AuditDiff.md`; `temp/` is Git-ignored and inspected directly. No commits, branch switch, push, merge, tag, release or GitHub modification. ADR-008, ADR-009, Master Design and Runbook were read completely and remain byte-for-byte unchanged against PRE-0 SHA-256 (`AuthorityBaseline.md`). R00 reconciled historical context before implementation.

## Patches and gates

| Patch | Outcome | Principal evidence |
|---|---|---|
| P91 / v0.9.1 | PASS | Public batch contracts, preflight/snapshot; 209 full offline PASS |
| P92 / v0.9.2 | PASS after owner-authorized narrow live study | Restricted officially documented Place ID namespace, conservative sidecar; 223 full offline PASS; `P92IdentityEvidence.md` |
| P93 / v0.9.3 | PASS | Sequential execution, safe failures and critical prefix; 231 full offline PASS |
| P94 / v0.9.4 | PASS | Pure exact interquery selection/provenance, no merge; 243 full offline PASS |
| P95 / v0.9.5 | PASS | Confirmed 2–3-query CLI, separate CSV/XLSX, no overwrite; 260 full offline PASS |
| P96 / v0.9.6 | PASS OFFLINE / OWNER ACCEPTANCE PENDING | 262 full offline PASS; G01–G22 PASS; G23 pending |

## Public behavior and compatibility

`ProspectorEngine.search_many()` accepts 1–5 validated, ordered `BatchQuery` values, snapshots all requests before browser startup and executes one source/normalization path per query with independent limits and runtime cleanup. `BatchSearchResult` retains each complete individual `SearchResult`, status, safe failure, duration, export selection and observation provenance. Exact `(source, kind, value)` identity from a verified Google Place ID suppresses only a *later-query* export observation. Unknown identities and repetitions inside one query remain exportable. No commercial field merge or historical lookup occurs. Unexpected errors/unsafe cleanup stop with a completed prefix. Individual `search()` and legacy wrapper behavior remain covered by regression tests.

CLI `Multiple Searches` accepts two or three requests with full summary/confirmation before execution. Its batch exports select only normalized rows; each valid query receives a separate collision-protected CSV/XLSX file with the seven historical columns, including a header-only file when fully suppressed. `FAILED` receives none; IO failures are reported without declaring export success. The individual CLI/export route is retained.

## Validation and acceptance matrix

Baseline: 151 unit, 34 integration, 185 full offline PASS, one live E2E deselected. Final P96: `compileall` PASS; 194 unit PASS; 68 integration PASS; 262 full offline PASS, one live E2E deselected; `git diff --check` PASS. JUnit files `P96-unit.xml`, `P96-integration.xml`, `P96-full.xml` record zero selected-test failures/errors. The initial sandbox Chromium `spawn EPERM` was infrastructure-only and passed when local Chromium was permitted. P91 `None` limit and P95 whitespace defects were corrected and all dependent gates repeated. No subsequent regression remains. `ValidationMatrix.md` details G01–G22 PASS with test references. G23 is **PENDING OWNER LIVE AUTHORIZATION**; the exceptional P92 live identity study did not run G23 or general E2E.

## Risks and limitations

Identity coverage is intentionally narrow: only the documented/observed Place ID form with strict candidate-to-panel evidence is verified. Missing, ambiguous, changed or unknown tokens remain `UNVERIFIED` and are exported, so duplicates can remain rather than be suppressed unsafely. Google Maps live variability, catalog completeness, 100-result production throughput and general owner acceptance are unproven for v0.9.x. Contact/about and certain website metadata limitations predate this patch line. The DATRA scenario is synthetic, not campaign/history matching. No known blocking defect or unresolved normative contradiction was found.

## Scope and owner action

`AuditDiff.md` lists every tracked/untracked source, test and documentation change by patch. No unexpected file, new dependency, API, persistence, DB, campaign/history integration, concurrent execution, field merge, thirteenth Business field, scraper rewrite or authority edit. The owner should review the completed offline evidence and decide whether/when to authorize the *separate* G23 live acceptance gate. No release or acceptance is implied by P96 PASS.

## v0.9.7 owner decision — current final state

The owner accepted P91–P96 and G01–G22 offline (194 unit, 68 integration, 262 full PASS, one E2E deselected), reproduced the offline results manually, and accepted two later full real-CLI batches as **G23 PASS / OWNER LIVE ACCEPTED**. The six corresponding CSV files were located locally; read-only inspection confirmed the seven approved columns and 94/95/83 rows for Run A and 30/40/50 for Run B. The owner reported Run A cross-query suppression of 0/5/2 and q03 `PARTIAL` with 85 observed/83 exportable/2 suppressed; Run B had no applicable suppression. The P92 identity study was separate from G23. No additional Google Maps call was made in v0.9.7.

The owner accepts possible commercial duplicate exports where identity is `UNVERIFIED` (observed `JJR S.A. DE C.V. - SERVICIOS LOGÍSTICOS TIJUANA`). This is **KNOWN ACCEPTED LIMITATION**, not a blocking bug or authorization for heuristic matching. No active blockers remain. v0.8.x is `OWNER ACCEPTED` with historical N31 paired-live-inspection caveat; v1.0.0 is NEXT for final hardening and stable-release preparation. Documentation-only commit/push status is recorded in the acceptance closure act. No code, tests or dependencies were changed by v0.9.7.

The v0.9.7 documentation-only commit is `71cb7f8981281ce68a2e9936ba01554e69e8c7ed`, pushed to `origin/v0.9.0`; final Git worktree is clean. No tag or release was created.

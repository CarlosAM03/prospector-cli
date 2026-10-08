# v0.7.x final architecture audit (autonomous run)

> The first-run audit below is preserved as historical evidence. The current closure audit follows in **Closure continuation from e266e74**.

## Evidence

- Initial/final HEAD: `ea7971b7bf3e4d3382debb6ee97c89f49b46bbd3`; branch `main`; no commit, tag, push or PR.
- Baseline deterministic regression: `20 passed, 1 deselected` with fresh pytest base directory and local Chromium permission.
- Final: `.venv-audit/Scripts/python.exe -m compileall -q src` exit 0; final unit suite `85 passed`; controlled integration suite `10 passed`; full `.venv-audit/Scripts/python.exe -m pytest -q --basetemp=temp/audit_runtime/pytest-v07x-final2` exit 0, `95 passed, 1 deselected`; `git diff --check` exit 0. LF/CRLF advisories were non-failing Git warnings.
- The deselected test is the opt-in Google Maps live E2E. Live calls and capacity measurements: **NOT EXECUTED — AUTHORIZATION REQUIRED**.

## Boundary review

| Boundary | Observed implementation | Status |
| --- | --- | --- |
| Google Maps | Delayed readiness, finite scroll/time/idle budgets, ordered source href tracking, identity-gated detail merge, valid partial preservation. No verified empty marker was invented. | Controlled offline evidence only; live DOM variability remains |
| Configuration | `EngineConfig` contains only limit/headless/website-enrichment flags. `resolve_limit` enforces positive values and an owner-supplied maximum without clamping. | Mechanism tested; operational maximum unapproved |
| Browser Runtime | One context owns Playwright/browser/Maps pages, closes on success/failure and preserves an original exception over cleanup failure. No pooling. | Tested offline |
| Logging | Module loggers diagnose feed/runtime/optional website failures; no root logger configuration. CLI prints remain presentation. | Tested offline |
| Error Model | Private issue collector can carry detail/website evidence. Existing `SearchResult` and exports remain unchanged. Fatal paths still use existing heterogeneous exceptions. | Public issue/typed exception schema blocked by mandatory design gate |
| ProspectorEngine | Facade consumes config, delegates only Google Maps, passes headless/enrichment flags, returns source `SearchResult` in controlled tests, rejects absent maximum before browser I/O. No CLI/export dependency. | Provisional, cannot operate with unset production maximum |
| CLI | Still calls `search_businesses(query, limit=500)`; controlled test confirms input/query/output and the historical 500 request. `ExportService` remains separate. | Migration and user limit input blocked by unresolved max/error contract |
| Models and exports | `SearchQuery`, `Business`, `SearchResult` and `total_found` unchanged; CSV/XLSX mapping unchanged; controlled export tests pass. | Preserved in deterministic suite |
| Version boundaries | No new source, normalization, business deduplication, multi-input, browser pooling, concurrency, API, SaaS or package separation was added. | Preserved in source audit |

## Code audit findings and limits

The Maps implementation deliberately prefers omitting uncertain detail over assigning another Business's fields. A changing Maps DOM/URL could therefore reduce enrichment or cause bounded indeterminate failure; offline fakes cannot quantify that rate. A verified empty-state selector/evidence is still absent. The pipeline does not claim Google Maps catalog completeness.

The private issue draft is not exposed through `SearchResult`; thus recoverable errors are not yet inspectable through the approved target public contract. The provisional facade's unsupported-source `NotImplementedError` is not the final typed taxonomy. These are known contract gaps, not validated release behavior.

No local Git commit was created because integrated files span multiple patches and the required public policies/live evidence remain unresolved. Versioned changes are limited to authorized source, tests, README and official docs; local implementation reports are under ignored `temp/Planeacion/v0.7.x/`.

## Required decisions before closure

1. Approve an evidence-based `engine_max_limit` value or equivalent determinable Engine policy, and resolve any conflict with the CLI's historical request of 500.
2. Ratify the public issue representation, collection/propagation semantics and fatal typed exception categories for v0.7.5; then integrate them into `SearchResult`, facade and CLI.
3. Authorize specific live Google Maps E2E and capacity batches under H07 if external stability/capacity acceptance is required.

Until then the overall v0.7.x line is **PROVISIONAL / BLOCKED FOR RELEASE ACCEPTANCE**, despite the green deterministic regression.

## Closure continuation from e266e74 — 2026-10-04

Initial closure HEAD `e266e74d8c2942a2f0c46cc00eef29b44c352eb1`, branch `main`, initially clean. No Master Plan, Decision Record or Runbook modification. C01–C08 applied; no maximum or release approval invented.

| Area | Verified outcome | Limit |
| --- | --- | --- |
| H-01 detail fields | Optional values equal to the prior panel are withheld. The deterministic contamination test failed before the fix and passes after. | Live detail remained unverified; recorded metrics cannot isolate why. |
| H-02 virtualization | Bounded bidirectional revisit finds only the exact saved href; failed revisit retains the summary. Controlled two-candidate integration passes. | Deep virtualization may exceed the small recovery budget. |
| H-03 selectors | Wait returns a specific visible nth locator and preserves semantic fallback. Hidden/visible sibling test passes. | Current Maps selectors still require monitoring. |
| H-04 budgets | Navigation has a finite 50-second budget; feed has attempt/time/idle budgets and bounded attribute/hover reads; detail click and reads use the remaining eight-second budget. | `mouse.wheel` has no Playwright timeout parameter; C05 enforced an outer 180-second process cap. |
| Error Model | Frozen `SearchIssue`, trailing `SearchResult.issues`, safe static messages, per-execution collector and chained typed Engine fatal errors. Wrapper exceptions remain legacy. | Internal exception text is not exposed in public issue messages. |
| Config/Engine | Requested/default/maximum separate; Engine rejects unset maximum before browser I/O, delegates Maps, no CLI/export dependency. | `engine_max_limit` remains unapproved. |
| CLI/export | CLI calls Engine, default 50, validates input, displays issues/errors; ExportService remains separate with unchanged CSV/XLSX columns. Wrapper default 50 and nonpositive behavior remain. | CLI cannot perform a normal search until maximum approval. |
| Runtime/logging | BrowserRuntime owns Playwright/browser/Maps pages. Module loggers do not configure root logging. | Two live graceful closes; one forced timeout left graceful cleanup unverified. |
| Version scope | No v0.8 normalization, v0.9 business deduplication/multi-input, SaaS/API, concurrency, pooling or physical package split. | Preserved. |

C05 started three exact Tijuana combinations only: limit 3 returned 3 in 32.502 s, limit 10 returned 10 in 86.707 s, limit 25 hit the 180-second hard cap. Orders 4–8 were not initiated. All 13 Businesses in completed runs retained summary fields with detail identity issues. The sample cannot establish a reliability rate, source completeness, San Diego behavior or a safe full-pipeline maximum. See `PilotC05-Report.md`.

**Current final status:** public Error Model and structural Engine/CLI integration implemented and offline validated; v0.7.x release acceptance **BLOCKED** on `engine_max_limit` and external detail/capacity evidence. Definitive maximum requires human approval. No push, tag, release or PR.

## Superseding documentation closure — 2026-10-05

The blocked status immediately above is retained as the outcome of the earlier audit stage and is no longer the current repository state. Later human approval established Engine maximum 100 and CLI default 50; corrective work restored detail and pipeline operation; the owner then completed two manual search/export smoke runs. The accepted technical baseline is `ee6b69e90972fce62fb5f9cedcee23acbd3c6b15`, integrated directly in `main`.

The architecture at that baseline preserves BrowserRuntime ownership, module logging, the public Error Model, `ProspectorEngine`, the migrated CLI, legacy wrapper compatibility, and the CSV/XLSX schema. Offline closure verification passed 113 unit, 28 integration, and 141 total tests with one live E2E deselected. No live call was made during documentation closure.

Current transition verdict: **v0.7.x accepted technical baseline; ready for formal v0.8.0 design input**. This is not a release tag, a universal live guarantee, or approval of a normalization design.

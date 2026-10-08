# v0.7.x final acceptance engineering audit — 2026-10-05

## Baseline and authority

- Repository: `CarlosAM03/prospector-cli`; branch `review/v0.7x-integration`.
- Initial HEAD: `e00960853b25fb417ca4a8cf7c82017ecff8d419`; clean working tree.
- Governing local inputs: `PlanMaestroV0.7.x.md`, autonomous runbook, v0.7.1 Gate B record/design/matrix/plan, and v0.7.x implementation/pilot/validation records. None was changed to justify this correction.
- Owner-approved policy: Google Maps Engine maximum 100, CLI default 50, valid requested range 1–100; legacy wrapper retains its earlier input contract.

## Owner-run smoke evidence and inspected exports

The owner reported two manual live CLI executions after the prior corrective refactor. This audit did not call Google Maps and did not repeat C05.

| Search | Owner-reported outcome | Local export inspection |
| --- | --- | --- |
| Maquila / Tijuana, limit 75 | 75 Businesses, 323.51 s, 5 recoverable issues (1 identity, 1 panel, 3 website), CSV export | `google_maps_maquila_tijuana_20261004_043211.csv`: 75 rows; 75 nonempty names/addresses, 67 phones, 44 websites, 16 emails; no duplicate or empty names. |
| Hospitales / Tijuana, default 50 | 50 Businesses, 187.87 s, 1 website issue, XLSX export | `google_maps_hospitales_tijuana_20261004_043643.xlsx`: 50 rows; 50 nonempty names/addresses, 46 phones, 37 websites, 20 emails; no duplicate or empty names. |

Both exports retain `Name, Category, Address, Phone, Email, Website, Language`. Issue counts and durations come from the owner, not from the export files. Neither run establishes source catalog completeness, an empty-state marker, universal reliability, or certified capacity at 100.

## Data integrity triage

### A-01 Category

Three of the 75 CSV categories (`C. Pacifico 9030`, `Avenida Universidad 102`, `C. 5 Sur 155`) exactly repeat the first segment of the same row's full address. `parse_business_summary` previously elected the first non-phone part of a later summary block as category, even when the source card supplied an address without an identifiable category. This is a demonstrated ambiguity and incorrect output for the three observed rows. A narrow post-detail reconciliation now clears a numeric category only when the same Business has an address beginning with that exact segment followed by a comma. It preserves unrelated and unsupported categories; it does not classify addresses generally or infer a missing category. Controlled unit and pipeline tests cover the three examples, normal categories, missing address evidence, order and identity.

### A-02 Email

The CSV contains `%20sales@ana-global.com` and `974-9586impex@mcna.com.mx`. Raw site HTML was not retained, so their exact source attributes cannot be proven from the export. A deterministic test reproduced the first output from `mailto:%20sales@ana-global.com`: the extractor matched the URL escape as part of the local name. The extractor now decodes percent escapes in `mailto:` links before matching, with no general email correction or validation system. The second value is compatible with text that concatenated a phone suffix and email, but it could also be a literal local name. Its provenance and intended correction remain unverified; no automatic split was introduced.

### A-03 Business association

The exports do not contain source href/place ID, so they cannot prove identity association row by row. No duplicate/empty names or direct cross-row contamination was observed in the inspected outputs. Existing controlled tests cover exact source IDs, equal names with distinct IDs, old/mismatched panels, changing URL identity, recycled links, consecutive Businesses and shared/stale optional fields. No confirmed identity-mapping defect was found in this audit. The owner-reported recoverable detail issues are consistent with conservative preservation of summaries, not proof of misassociation.

## Patch contract audit

| Patch | Evidence and status |
| --- | --- |
| v0.7.1 | Navigation/readiness, bounded virtual-feed capture, source identity, safe detail, partial results and distinct stall/end behavior remain covered by deterministic tests and the two observed live searches. No source-total claim. |
| v0.7.2 | Engine maximum 100, CLI default 50, 1–100 validation and explicit over-limit rejection before browser use remain tested; wrapper is uncapped. |
| v0.7.3 | One BrowserRuntime per execution, cleanup, original exception preservation and no double close are covered by controlled tests; no pooling/concurrency. |
| v0.7.4 | Module logging is separate from CLI presentation; no extraction-layer print calls found. |
| v0.7.5 | Frozen SearchIssue, independent SearchResult.issues, safe recoverable messages, typed fatal categories and preserved Businesses remain covered. |
| v0.7.6 | ProspectorEngine owns reusable orchestration without CLI or ExportService imports. |
| v0.7.7 | Interactive default/maximum/invalid input, issue summary, CSV/XLSX and legacy wrapper remain covered; both export types were observed in owner-run smoke tests. |

## Validation and release boundary

- Initial offline suite at e009608: 137 passed, 1 opt-in live E2E deselected.
- Final source compile: passed. Unit: 113 passed. Integration: 28 passed. Complete default suite: 141 passed, 1 opt-in E2E deselected. `git diff --check`: exit 0, with only Windows LF/CRLF advisories.
- No live tests, capacity experiment, push, merge, tag or release in this audit.
- Engineering recommendation: accept v0.7.x for owner review if final offline gates remain green. Final acceptance is the owner's decision.

## Handoff to v0.8.0

The Master Plan reserves formal deterministic field normalization for v0.8.0. This audit confirms no additional anomaly that must be moved there: the address-as-category output was a narrow v0.7.x parsing error, and percent-encoded `mailto:` handling was an extraction error. The unusual `974-9586impex@...` output lacks source provenance, so it is an open observation rather than an approved normalization rule. Do not infer a phone/email split, new validation schema or deduplication from it. Keep v0.9.x multi-input and business deduplication outside v0.8.0.

---

## Documentation closure and transition baseline — 2026-10-05

### Closure status

`ee6b69e90972fce62fb5f9cedcee23acbd3c6b15` is the accepted technical baseline of the v0.7.x line and the starting point for formal v0.8.0 planning. At this documentation audit, local `main`, `origin/main`, `review/v0.7x-integration` and the current `v0.8.0` branch resolve to that commit. History contains no separate merge commit for the acceptance baseline; integration occurred by direct/fast-forward history. No tag or release is asserted.

The current branch name is `v0.8.0`; the requested expected name was `planning/v0.8.0`. This audit did not rename or create branches. The tree was clean before documentation edits.

### Final baseline history

| Milestone | Commit | Evidence role |
| --- | --- | --- |
| Prior operational baseline | `ea7971b7bf3e4d3382debb6ee97c89f49b46bbd3` | Pre-v0.7.x architecture reference |
| First autonomous implementation | `e266e74d8c2942a2f0c46cc00eef29b44c352eb1` | Initial seven-patch implementation checkpoint |
| Corrective integration | `545329ed9d219987c12d368d2f4950704586506c` | Error Model, Engine/CLI integration and pilot findings |
| Operational reconciliation | `e00960853b25fb417ca4a8cf7c82017ecff8d419` | Limit policy, detail/feed recovery and release candidate |
| Technical acceptance | `ee6b69e90972fce62fb5f9cedcee23acbd3c6b15` | Data-integrity fixes and final acceptance audit |

### Approved decisions now in force

- Gate B H01–H07 and P-01/P-02 remain the governing v0.7.1 decisions.
- Public Error Model decisions C01–C03 are implemented through frozen `SearchIssue`, `SearchResult.issues`, recoverable issue collection and typed fatal exceptions.
- Google Maps Engine policy: maximum 100; CLI default 50; Engine requests 1–100; over-limit requests fail before browser startup and are never silently clamped.
- The transitional `search_businesses(query, limit=50)` wrapper preserves its approved legacy behavior, including nonpositive values and no retroactive Engine maximum.
- Browser ownership is one `BrowserRuntime` per execution; no pooling or concurrency.
- Candidate identity tracking is traversal state, not business deduplication.
- No reliable live Google Maps empty/end marker has been established; valid partial results are preserved and uncertainty is reported.

### Definitive patch status

| Patch | Purpose and implemented scope | Main components | Preserved contracts and evidence | Accepted limitations / deferred work |
| --- | --- | --- | --- | --- |
| v0.7.1 | Stabilize navigation, delayed selectors, virtual feed, safe detail enrichment, website merge and bounded partial outcomes. | `navigation/`, selector/LazyCharge, `scraper/google_maps/`, timing helper; focused unit/integration tests. | Discovery order, source identity, summary preservation, `total_found`, legacy nonpositive limit, CSV/XLSX. Controlled feed/detail/website tests plus owner-run searches. | External DOM variability; no verified source-end marker; no catalog-completeness claim. |
| v0.7.2 | Introduce minimal immutable configuration and separate requested/default/maximum limits. | `engines/config.py`, Engine/CLI call sites and tests. | `EngineConfig(limit, headless, website_enrichment)`; explicit validation; no clamp; wrapper unaffected. | Maximum 100 is an approved operating policy, not statistical capacity certification. |
| v0.7.3 | Make Playwright/browser/page ownership explicit and guarantee cleanup. | `engines/browser_runtime.py`, navigation page factory, scraper orchestration and runtime tests. | One runtime per execution; exception preservation; no double close, pool or concurrency. | Forced external process termination cannot prove graceful application cleanup. |
| v0.7.4 | Separate reusable diagnostics from CLI presentation. | Module loggers in runtime/feed/website path; CLI presentation unchanged. | No root logging policy; `print` remains confined to CLI presentation. | Logging configuration remains consumer-owned. |
| v0.7.5 | Complete recoverable/fatal Error Model. | `models/search_issue.py`, `models/search_result.py`, `engines/errors.py`, `issue_collector.py`, pipeline propagation and tests. | Safe immutable issues, independent issue lists, ordered Businesses, typed fatal boundaries and exception chaining. | External failures remain source-dependent; public messages intentionally omit sensitive diagnostics. |
| v0.7.6 | Establish reusable `ProspectorEngine(config).search(query)` facade. | `engines/prospector_engine.py`, config/source orchestration and tests. | Returns `SearchResult`; no CLI or ExportService dependency; only Google Maps supported. | Additional sources and physical Engine packaging are future scope. |
| v0.7.7 | Migrate CLI to Engine and retain exports and wrapper compatibility. | `src/main.py`, facade/config integration, CLI and export regression tests. | Optional 1–100 input, default 50, readable fatal/issues output, unchanged seven-column CSV/XLSX, legacy wrapper. | Interactive presentation remains in `main.py`; no release/tag created. |

### Test and operational evidence

- Historical checkpoints remain valid only for the code state and purpose recorded in each document.
- This documentation audit reran only offline checks at `ee6b69e`: source compilation passed; 113 unit tests passed; 28 integration tests passed; full default suite passed 141 tests with 1 opt-in live E2E deselected.
- Owner smoke A: `Maquila`, Tijuana, limit 75, 75 Businesses, 323.51 seconds, 5 recoverable issues, CSV.
- Owner smoke B: `hospitales`, Tijuana, default 50, 50 Businesses, 187.87 seconds, 1 recoverable issue, XLSX.
- The smoke runs establish operation for those observations. They do not establish universal field accuracy, catalog completeness, permanent website availability, DOM stability or statistically certified capacity at 100.

### Historical contradictions and resolution

The Master Plan, Runbook, Gate B documents, implementation checkpoints, C05 protocol/report and early sections of the progress/blocker/audit records describe the state at their creation. Statements such as “maximum unresolved,” “CLI blocked,” “limit=500,” “public Error Model pending” and “no live execution” are **HISTORICAL**, not CURRENT. They are preserved for traceability and superseded by the dated continuation sections, code at `ee6b69e`, owner decisions and this closure record. The Master Plan and decision records were not edited retrospectively.

`PlanProspectorCLIv1-0-0.md` is useful historical planning context. Its concrete v0.8.0 class/module examples and phase sequence are proposals, not an approved v0.8.0 design. No patch count, integration point or normalization rule is approved by this closure.

### Resolved blockers and remaining limitations

Resolved: numerical Engine policy; CLI route; public Error Model; detail false negatives found by C05; bounded feed behavior; category/address parsing defect; percent-encoded `mailto:` extraction defect; manual operational evidence.

Remaining nonblocking limitations: external Maps variability, no verified source-end/empty marker, sequential execution cost, incomplete contact/about/content-type metadata, and the unproven origin of `974-9586impex@mcna.com.mx`. The last value is evidence for future analysis, not authorization to rewrite it.

### Transition decision

v0.7.x is technically closed as the baseline for planning. Formal v0.8.0 design may begin under the approved version boundary “deterministic normalization after extraction/enrichment.” The preliminary documents in `temp/Planeacion/v0.8.0/` are research inputs only; they do not approve architecture, patches, implementation or acceptance criteria.

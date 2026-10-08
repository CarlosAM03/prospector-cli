# ADR-010 — Stable CLI UX, Windows Portable Distribution and v1.0.0 Release Freeze

**Status:** APPROVED  
**Target:** Prospector CLI `v1.0.0`  
**Date:** October 2026  
**Owner:** Carlos Armenta  
**Predecessor:** Prospector CLI `v0.9.x — OWNER ACCEPTED / COMPLETE`  
**Accepted v0.9.x implementation baseline:** `c7193d55a36618e934e29a9678b3f9b01e9b6543`  
**v0.9.x documentation closure:** `71cb7f8981281ce68a2e9936ba01554e69e8c7ed`

---

# 1. Decision Summary

Prospector CLI `v1.0.0` SHALL be the first stable, distributable and user-facing release of the existing accepted Prospector CLI product.

`v1.0.0` SHALL NOT introduce new prospecting capabilities.

The release line is limited to:

- final hardening;
- stabilization;
- formal CLI UX;
- runtime observability for the user;
- Windows portable packaging;
- clean-environment validation;
- contract freeze;
- release documentation;
- first stable GitHub release.

The functional prospecting behavior accepted in `v0.9.x` remains authoritative.

After successful `v1.0.0` release, Prospector CLI enters a maintenance/frozen state while future architectural development moves toward physical Prospector Engine extraction and later API consumers.

---

# 2. Context

Prospector CLI completed its functional development line through `v0.9.x`.

The accepted implementation already provides:

- Google Maps prospect extraction;
- detail-panel enrichment;
- Website Engine enrichment;
- deterministic global normalization;
- single-query execution;
- sequential multi-query execution;
- verified-identity interquery deduplication;
- original and normalized result views;
- typed recoverable/fatal error semantics;
- CSV and XLSX export;
- isolated browser lifecycle per query;
- batch provenance;
- offline regression coverage;
- owner-accepted live execution.

The remaining gap before `v1.0.0` is therefore not functional scope.

The remaining gap is converting the accepted implementation into a stable application that can be distributed and used by a Windows user without requiring the development repository or Python environment.

---

# 3. v1.0.0 Scope Freeze

The functional scope is frozen.

`v1.0.0` SHALL preserve the accepted behavior of:

- `ProspectorEngine.search()`;
- `ProspectorEngine.search_many()`;
- `EngineConfig`;
- `SearchQuery`;
- `SearchResult`;
- `BatchQuery`;
- `BatchQueryResult`;
- `BatchSearchResult`;
- `Business`;
- `NormalizedBusiness`;
- `SearchIssue`;
- current typed fatal errors;
- current Google Maps source behavior;
- current normalization behavior;
- current verified-identity deduplication;
- current limit policy;
- current sequential execution;
- current seven-column CSV/XLSX schema.

The seven-column export contract remains:

```text
Name
Category
Address
Phone
Email
Website
Language
```

Hardening MAY fix demonstrated defects.

Hardening SHALL NOT silently redefine accepted business rules or Engine semantics.

---

# 4. Explicit Non-Goals

The following are OUT of scope:

- additional prospect sources;
- new prospecting engines;
- new enrichment capabilities;
- historical deduplication;
- heuristic business matching;
- field merge between duplicates;
- campaigns;
- CRM;
- persistence/database;
- queues;
- jobs;
- parallel query execution;
- distributed execution;
- SaaS;
- FastAPI;
- multi-tenancy;
- new normalization policy;
- Engine extraction into a separate package;
- plugin architecture;
- auto-update;
- remote analytics;
- remote telemetry;
- checkpoint/resume;
- partial-result persistence.

These concerns require future ADRs.

---

# 5. Architectural Boundary

The accepted architecture remains:

```text
User
 |
 v
Prospector CLI
 |
 | presentation / interaction
 v
ProspectorEngine
 |                 |
 | search()        | search_many()
 |                 |
 +--------+--------+
          |
          v
source-specific extraction
          |
          v
global normalization
          |
          v
SearchResult / BatchSearchResult
          |
          v
ExportService
```

The CLI remains a consumer/adapter of the Engine.

User presentation SHALL NOT migrate into:

- Google Maps scraper;
- Website Engine;
- normalization;
- deduplication;
- domain models;
- source-identity logic.

Packaging concerns SHALL NOT become prospecting-domain behavior.

---

# 6. Formal CLI Redesign

The current development-oriented interface SHALL be replaced by the first formal Prospector CLI user interface.

The final interface SHALL be:

- professional;
- visually coherent;
- readable;
- predictable;
- keyboard-oriented;
- suitable for repeated execution;
- explicit about current state;
- free of unnecessary diagnostic noise.

The application SHALL behave like an end-user application rather than a development script.

---

# 7. CLI UI Technology

**Decision: Rich SHALL be used as the terminal-presentation library.**

Rich was selected because it provides:

- progress bars;
- indeterminate progress;
- multiple concurrent progress tasks;
- tables;
- panels;
- status/spinner presentation;
- live dynamic terminal output;
- structured formatting;

without requiring Prospector CLI to become a full event-driven TUI application.

Rich SHALL be a presentation-layer dependency only.

The following SHALL NOT import Rich:

- `ProspectorEngine`;
- Google Maps pipeline;
- Website Engine;
- Normalization Engine;
- deduplication;
- domain models.

The Engine SHALL emit neutral state/metrics.

The CLI SHALL convert those neutral events into Rich presentation.

---

# 8. Main Application Lifecycle

Launching the packaged executable SHALL enter the main application.

Conceptually:

```text
============================================================
                     PROSPECTOR CLI
                       v1.0.0
============================================================

  1. New Search
  2. Multiple Searches
  3. Exit

Select an option >
```

Exact styling remains an implementation concern.

The application remains active until the user explicitly exits or a fatal unrecoverable application condition requires termination.

---

# 9. Repeated Execution

A user SHALL be able to:

```text
launch
  -> search
  -> inspect summary
  -> inspect results if desired
  -> export
  -> perform another search
  -> repeat
  -> return to menu
  -> exit
```

The executable SHALL NOT need to be relaunched between searches.

---

# 10. Input Navigation

Before execution starts, the user SHALL be able to:

- return to the previous view;
- correct keyword;
- correct location;
- correct limit;
- revise batch queries;
- cancel the operation;
- return to main menu.

No source execution SHALL begin before final confirmation.

---

# 11. Input Confirmation

Both workflows require explicit confirmation:

- single search;
- multiple searches.

After confirmation, the configuration SHALL be displayed before browser creation.

Once execution begins, inputs SHALL be immutable for that execution.

If the user rejects confirmation, inputs may be edited because the source pipeline has not started.

---

# 12. Effective Configuration View

Before execution the CLI SHALL show the effective configuration, including at least:

- source;
- keyword;
- location;
- requested limit;
- website enrichment state;
- browser visibility mode;
- number of batch queries when applicable.

No persistent user-preference system is introduced.

The configuration shown applies only to the current execution/session.

---

# 13. Browser Visibility

Immediately after query confirmation and before `BrowserRuntime` is created, the CLI SHALL allow the user to select:

```text
Browser mode

1. Background
2. Visible
```

The target default is:

**Background / headless.**

However, this default is subject to the v1.0.0 headed-vs-headless equivalence gate defined later in this ADR.

If background execution does not satisfy equivalence requirements, visible Chromium SHALL become the stable default while background remains optional where safe.

Failure of headless equivalence alone SHALL NOT block `v1.0.0` if headed execution remains reliable.

---

# 14. Website Enrichment

Website enrichment remains part of the normal Google Maps source pipeline.

For the `v1.0.0` CLI:

**Website enrichment SHALL remain enabled.**

It SHALL NOT be exposed as an end-user feature toggle.

This preserves the accepted product behavior instead of creating a new configuration surface.

---

# 15. Single Search Flow

The final single-search workflow SHALL conceptually be:

```text
Main Menu
   |
   v
New Search
   |
   +-- keyword
   +-- location
   +-- limit
   |
   v
Review
   |
   +-- edit/back
   +-- confirm
   |
   v
Browser mode
   |
   v
Effective configuration
   |
   v
Execute
   |
   v
Live Progress
   |
   v
Search Summary
   |
   +-- View Results
   +-- Export
   +-- Back
```

---

# 16. Batch Search Flow

The existing CLI boundary remains:

- minimum two queries;
- maximum three queries interactively.

The Engine retains its approved broader 1–5 contract.

Conceptually:

```text
Main Menu
   |
   v
Multiple Searches
   |
   +-- Search 1
   +-- Search 2
   +-- optional Search 3
   |
   v
Review Batch
   |
   +-- edit/back
   +-- confirm
   |
   v
Browser mode
   |
   v
Effective configuration
   |
   v
Sequential Execution
   |
   v
Live Progress
   |
   v
Per-query summaries
   |
   v
Batch Summary
   |
   +-- View Results
   +-- Export
   +-- Back
```

---

# 17. Result Presentation

The terminal SHALL NOT automatically dump every Business after execution.

The first result surface SHALL be a summary.

The post-execution menu SHALL conceptually provide:

```text
1. View Results
2. Export Results
3. Back
```

Exact wording may change without altering the decision.

---

# 18. Result Pagination

If the user selects `View Results`, Businesses SHALL be displayed in groups of:

**10 records per page.**

The user SHALL be able to navigate through the result set without flooding the terminal.

The exported file remains the authoritative complete user output.

---

# 19. Post-Export Behavior

After export, the CLI SHALL ask whether the user wants to:

- perform another search;
- return to the main menu.

The application SHALL remain active unless the user chooses to exit.

---

# 20. Real-Time Execution UX

`v1.0.0` SHALL expose meaningful execution progress in real time.

This is a formal product requirement.

The purpose is to allow the user to understand what the application is doing even when Chromium is running in background mode.

The progress UI SHALL show macro state, not developer debugging output.

---

# 21. Two-Level Progress Model

The UX SHALL expose two conceptual levels:

## Global pipeline

Examples:

```text
Search 1 / 3
Google Maps extraction
Normalization
Interquery deduplication
Result assembly
Export
```

## Source-internal pipeline

For Google Maps, examples include:

```text
Navigation
Feed discovery
Detail enrichment
Website enrichment
Source completion
```

The distinction SHALL preserve the architecture:

```text
global pipeline != Google Maps internal pipeline
```

---

# 22. Hybrid Progress

Progress SHALL be hybrid.

When a real total exists:

**determinate progress MAY be shown.**

Example:

```text
Detail enrichment    31 / 50
```

When a meaningful total does not exist:

**indeterminate state SHALL be shown.**

Example:

```text
Feed discovery       Working...
```

Fake percentages SHALL NOT be displayed.

---

# 23. Execution Metrics

The CLI SHALL present structured execution metrics.

The target metrics are:

- requested limit;
- Google Maps candidates observed;
- Businesses extracted;
- Businesses normalized;
- verified identities;
- unverified identities;
- duplicates suppressed;
- exportable/final Businesses;
- recoverable issues;
- total query execution time;
- stage timing where meaningful;
- total batch execution time.

---

# 24. Maps Observed vs Extracted

The CLI SHALL distinguish:

```text
Maps candidates observed
```

from:

```text
Businesses extracted
```

These are different metrics and SHALL NOT be merged into an ambiguous “results found” counter.

Example:

```text
Maps candidates observed : 64
Businesses extracted     : 50
Businesses normalized    : 50
Duplicates suppressed    : 5
Final exportable         : 45
```

---

# 25. Metrics Semantics

Metrics shown to the user SHALL be:

- exact when exact;
- clearly named;
- source-aware where appropriate;
- derived from actual execution state;
- never fabricated from expected progress.

A stage metric that cannot be measured reliably SHALL not be shown as a precise number.

---

# 26. Existing Metrics Baseline

The current implementation already contains an internal `metrics_sink` in the Google Maps pipeline.

It currently captures information including:

- browser version;
- navigation time;
- feed time;
- observed candidates;
- detail time;
- detail unchanged count;
- Website Engine time;
- cleanup completion.

`v1.0.0` SHALL evolve this existing instrumentation rather than introduce an unrelated second metrics system.

---

# 27. Execution Observability Contract

A neutral execution-observability mechanism SHALL be introduced.

Conceptually it may include:

```text
ExecutionEvent
ExecutionMetrics
ExecutionObserver
ExecutionSummary
```

Exact naming is implementation design, not ADR contract.

The chosen pattern SHALL be event/callback-based rather than UI polling where practical.

The observer SHALL support a no-op implementation.

The Engine SHALL not depend on a CLI renderer.

---

# 28. Observability Visibility Boundary

The initial observability contract SHALL be:

**internal Engine infrastructure, not a frozen public Engine API in v1.0.0.**

This allows the CLI to consume structured progress without prematurely freezing an API that has not yet been exercised by the future extracted Engine/API consumers.

Post-v1 Engine extraction MAY promote a refined observability contract to public API.

---

# 29. No Telemetry in v1.0.0

Execution metrics SHALL be used for:

- user experience;
- local execution summaries;
- future engineering evaluation.

They SHALL NOT be:

- sent remotely;
- persisted as analytics;
- exported automatically;
- uploaded;
- associated with user identity;
- stored in a telemetry backend.

`v1.0.0` implements observability UX, not telemetry infrastructure.

---

# 30. Summary Model

Every completed query SHALL receive an execution summary.

Batch execution SHALL additionally receive a consolidated summary.

The summaries SHALL contain relevant metrics and status without exposing technical implementation noise.

---

# 31. User-Facing Status Model

The UI SHALL distinguish at least:

```text
SUCCESS
SUCCESS WITH ISSUES
PARTIAL
FAILED
BATCH INTERRUPTED
CANCELLED
```

Exact display labels may be humanized.

The underlying Engine semantic statuses SHALL not be silently changed for presentation.

---

# 32. Recoverable Issues

Recoverable issues SHALL be summarized clearly.

Detailed exception internals SHALL not normally be printed to the end user.

Diagnostics belong in logs.

---

# 33. Ctrl+C Semantics

`Ctrl+C` SHALL initiate controlled cancellation.

It SHALL NOT immediately terminate the application during an active execution.

The CLI SHALL present a confirmation similar to:

```text
Cancel current execution?

All unexported results from this execution will be lost.

[y/N]
```

If the user answers No:

- execution continues.

If the user answers Yes:

- graceful cancellation begins.

---

# 34. Cancellation Semantics

Confirmed cancellation means:

- current execution is aborted;
- browser/runtime cleanup is attempted;
- no checkpoint is created;
- no resume data is created;
- no partial Business state is persisted;
- unexported work is lost.

The application MAY return to the main menu after successful cleanup.

Cancellation is not a partial-results feature.

---

# 35. Console Window Close

Closing the terminal through Windows console-close behavior SHALL receive:

**best-effort cleanup.**

The application SHALL NOT promise the same interactive confirmation available through Ctrl+C because operating-system termination behavior may not permit a reliable user interaction window.

The release SHALL document the difference.

---

# 36. Logging

Application diagnostics SHALL be separate from normal CLI output.

Portable structure SHALL contain:

```text
logs/
```

Logs SHALL use bounded rotation rather than unlimited accumulation.

A small rotating set is preferred, conceptually:

```text
logs/
  prospector.log
  prospector.log.1
  prospector.log.2
```

Exact size/count limits belong to implementation design.

Logs SHALL NOT become a telemetry system.

---

# 37. Export Location

The portable distribution SHALL contain:

```text
exports/
```

Normal exports SHALL be written there by default.

The CLI SHALL clearly show the resulting filename/location.

---

# 38. Export Formats

Supported release formats remain:

- CSV;
- XLSX.

No new exporter is required.

Batch execution continues to produce independent files per valid query.

A valid zero-result export remains a headers-only file where the existing contract requires it.

---

# 39. Windows Distribution Requirement

The first official binary platform is:

**Windows 10 / Windows 11 x64.**

A Windows user SHALL NOT need:

- Python;
- pip;
- virtualenv;
- Playwright CLI;
- Git;
- repository checkout;
- manual dependency installation.

---

# 40. Portable Distribution

The primary release artifact SHALL be a self-contained portable ZIP.

Target shape:

```text
Prospector-CLI-v1.0.0-win64.zip
```

containing conceptually:

```text
Prospector-CLI/
├── prospector.exe
├── runtime / packaged dependencies
├── Chromium assets
├── exports/
├── logs/
├── LICENSE
├── third-party notices
└── user documentation
```

Exact generated directories may differ based on the selected packager.

---

# 41. Portable Behavior

After extraction, the user SHOULD be able to:

```text
open folder
-> execute prospector.exe
-> use application
```

without installation.

The extracted directory SHOULD be movable/copyable between compatible Windows machines.

Running from removable storage is desirable but is not a release blocker.

---

# 42. Packaging Technology

**Primary packaging candidate: PyInstaller.**

The preferred topology is:

**PyInstaller `onedir`.**

Reasons include:

- natural fit for portable ZIP distribution;
- easier inclusion of browser/runtime assets;
- easier troubleshooting;
- avoids unnecessary temporary extraction of a giant one-file binary;
- supports transparent resource layout.

`onefile` MAY be evaluated.

It SHALL NOT be selected merely because it produces one visible file.

Reliability has priority over aesthetics.

---

# 43. Chromium Packaging

Chromium SHALL be distributed with the portable package.

The end user SHALL NOT be required to execute:

```text
playwright install
```

or perform a first-run developer setup.

The package SHALL include the browser/runtime assets required by the supported Playwright version.

---

# 44. Browser Bundle Versioning

The packaged browser SHALL correspond to the Playwright version shipped by the release.

Browser/runtime mismatch SHALL be considered a release defect.

---

# 45. Headed and Background Support

Because the user may select:

- visible;
- background;

the portable distribution SHALL contain sufficient browser assets for the supported release modes.

Optimization to a headless-only runtime is not allowed unless it still satisfies the visible-browser product requirement.

---

# 46. Installer

An installer is OPTIONAL.

It is not a release gate for `v1.0.0`.

If implementation proves trivial and useful, it MAY be provided alongside the portable ZIP.

The portable ZIP remains the normative distribution.

---

# 47. Single Executable

A single physical `.exe` is desirable but NOT mandatory.

A stable portable directory containing:

```text
prospector.exe + required assets
```

fully satisfies the v1.0.0 distribution requirement.

---

# 48. Clean Environment Validation

The packaged application SHALL be validated outside the development environment.

At minimum:

```text
launch packaged application
-> main menu
-> single search
-> batch search
-> progress UI
-> result summary
-> CSV export
-> XLSX export
-> repeated search
-> Ctrl+C cancellation
-> normal exit
```

The clean environment SHALL not depend on the existing virtualenv or repository runtime.

---

# 49. Filesystem Validation

Validation SHALL include:

- normal non-administrator execution;
- paths containing spaces;
- execution outside repository root;
- exports directory behavior;
- logs directory behavior;
- repeated sessions;
- moving/copying portable directory;
- cleanup after failures.

Hardcoded development paths are release blockers.

---

# 50. Dependency Audit

Before release, dependencies SHALL be classified as:

- runtime;
- development/test;
- unused.

Only necessary runtime components SHALL ship.

Dependency changes during hardening require a concrete release reason.

---

# 51. Runtime Dependency Hygiene

The current dependency set SHALL be audited before packaging.

Large or unused libraries SHALL NOT automatically be removed solely to optimize package size if removal risks regressions.

Any cleanup requires regression evidence.

---

# 52. Security / Safety Hardening

Release hardening SHALL review at least:

- temporary-file handling;
- file overwrite behavior;
- path safety;
- runtime cleanup;
- exception leakage;
- stale/incomplete exports;
- browser lifecycle;
- packaged resource failures;
- logging exposure;
- cancellation cleanup.

No separate security framework is required.

---

# 53. Performance Hardening

No new performance architecture is introduced.

Sequential execution remains authoritative.

Performance work is limited to:

- detecting regressions;
- measuring meaningful stage times;
- identifying obvious avoidable overhead;
- ensuring the packaged build remains operationally comparable to source execution.

---

# 54. No Parallelization

The following remain OUT:

- threads for multi-query execution;
- multiprocessing;
- parallel browsers;
- queue workers;
- async batch orchestration.

UX progress SHALL NOT be confused with concurrency.

---

# 55. Code Signing

Commercial paid code-signing certificates are OUT of scope for `v1.0.0`.

The release MAY be unsigned.

An unsigned release SHALL still include SHA-256 hashes.

---

# 56. SignPath Foundation

SignPath Foundation MAY be evaluated as an optional free code-signing path.

It is:

**OPTIONAL / NON-BLOCKING.**

It SHALL only be used if:

- the project qualifies;
- usage remains free;
- setup is low-friction;
- integration does not materially delay release.

If SignPath requires disproportionate process/work, `v1.0.0` SHALL proceed unsigned.

---

# 57. Artifact Integrity

Release artifacts SHALL include SHA-256 checksums.

At minimum for the primary portable package:

```text
Prospector-CLI-v1.0.0-win64.zip
SHA-256: ...
```

---

# 58. No Auto-Update

`v1.0.0` SHALL contain no automatic update mechanism.

A future version is obtained by downloading another release artifact.

---

# 59. No Persistent Preferences

The CLI SHALL not persist:

- browser preference;
- export preference;
- last query;
- last location;
- last limit;
- UI choices.

Current execution configuration may be displayed but is session-local.

---

# 60. Version Presentation

The distributed CLI SHALL display:

```text
Prospector CLI
v1.0.0
```

The implementation SHOULD use one controlled version source where practical.

Duplicate independently maintained version literals SHOULD be avoided.

---

# 61. CLI Contract Freeze

After owner acceptance of the final CLI UX, the following become stable `v1.0.0` user contracts:

- main workflow structure;
- single-search behavior;
- multi-query behavior;
- confirmation semantics;
- current limits;
- export schema;
- result status semantics;
- verified-only dedupe semantics;
- cancellation semantics;
- output directory behavior.

Pure styling details are not frozen API.

---

# 62. Engine Contract Freeze

The following SHALL undergo final review before release:

```text
ProspectorEngine
EngineConfig
SearchQuery
SearchResult
BatchQuery
BatchQueryResult
BatchSearchResult
Business
NormalizedBusiness
SearchIssue
typed fatal errors
ExportService boundary
```

The objective is confirmation/freeze, not redesign.

A discovered need for a breaking redesign requires owner review.

---

# 63. Observability Contract Is Not Public Freeze

The new execution observer/event mechanism is explicitly excluded from the public Engine freeze for `v1.0.0`.

It remains internal infrastructure.

This avoids prematurely freezing a contract intended for future Engine/API consumers.

---

# 64. User Documentation

The stable release SHALL document:

- what Prospector CLI does;
- supported Windows versions;
- download;
- extraction;
- launch;
- main menu;
- single search;
- multiple searches;
- limits;
- progress indicators;
- browser visible/background mode;
- result summaries;
- result pagination;
- CSV/XLSX export;
- exports folder;
- logs folder;
- cancellation;
- known limitations;
- verified-identity dedupe semantics;
- troubleshooting;
- license.

---

# 65. Developer Documentation

Developer documentation SHALL separately describe:

- source setup;
- Python dependencies;
- tests;
- architecture;
- packaging;
- release process;
- contract boundaries.

User documentation SHALL not require development knowledge.

---

# 66. Third-Party Notices

The release process SHALL audit licenses/notices for distributed dependencies and Chromium/browser assets.

Required notices SHALL ship with the portable release.

Prospector CLI itself remains under its existing MIT license.

---

# 67. Release Artifacts

A successful stable release SHALL include:

```text
repository state for v1.0.0
Git tag v1.0.0
GitHub Release v1.0.0
portable Windows x64 artifact
SHA-256 checksum
release notes
LICENSE
required third-party notices
user documentation
```

An installer may additionally exist but is not required.

---

# 68. Release Freeze

After successful acceptance:

```text
v1.0.0
  |
  +-- contracts frozen
  +-- tagged
  +-- GitHub Release published
  +-- Windows artifact published
  +-- documentation published
  |
  v
Prospector CLI maintenance mode
```

---

# 69. Post-v1 Direction

After the CLI release, future architectural work moves toward:

```text
stable Prospector CLI v1.0.0
          |
          v
physical Prospector Engine extraction
          |
          +--> CLI consumer
          |
          +--> future API consumer
          |
          +--> future multitenant platform
```

This migration is explicitly post-v1.

---

# 70. FastAPI / SaaS Boundary

No FastAPI, SaaS, tenancy, distributed jobs or API server SHALL be introduced during the `v1.0.0` CLI release line.

The stable Engine boundary will later serve as the basis for those consumers.

---

# 71. Release Blockers

`v1.0.0` SHALL NOT release if any of the following remain:

- v0.9.x regression;
- broken `search()`;
- broken `search_many()`;
- unintended normalization change;
- unintended deduplication change;
- unintended export-schema change;
- unreliable browser cleanup;
- packaged application cannot execute the accepted pipeline;
- end user requires Python/developer setup;
- packaged application depends on repository paths;
- Rich UX corrupts execution behavior;
- cancellation leaves runtime in an unsafe state;
- clean-machine validation fails;
- public contracts remain knowingly unstable;
- release documentation contradicts behavior;
- mandatory third-party notices are unresolved;
- artifact integrity cannot be established.

---

# 72. Acceptance Categories

Final release acceptance requires five categories:

## A — Functional Regression

Accepted `v0.9.x` behavior remains intact.

## B — Final CLI UX

The formal interface, progress model, summaries, pagination, confirmation and cancellation are owner accepted.

## C — Portable Distribution

The Windows artifact works without Python/project setup.

## D — Clean Environment

Representative packaged workflows succeed on a clean supported Windows environment.

## E — Release Freeze

Contracts, docs, version, checksums, tag and release artifacts are complete.

All five categories SHALL pass.

---

# 73. Final v1.0.0 Workstreams

Implementation planning SHALL organize the release around four primary workstreams:

```text
1. FINAL HARDENING
   lifecycle
   filesystem
   cleanup
   errors
   dependency audit
   regression

2. FINAL CLI UX
   Rich
   navigation
   progress
   metrics
   summaries
   pagination
   cancellation

3. WINDOWS PORTABLE PACKAGING
   PyInstaller
   Chromium
   onedir
   clean-machine validation

4. RELEASE FREEZE
   contract audit
   versioning
   docs
   checksums
   tag
   GitHub Release
```

No feature-development workstream is authorized.

---

# 74. Consequences

## Positive

This decision:

- converts the accepted engine-backed CLI into a real end-user product;
- prevents feature creep before the first release;
- establishes a stable UX;
- provides meaningful progress with hidden Chromium;
- creates a portable Windows distribution;
- creates a frozen reference implementation;
- preserves architectural separation;
- provides useful internal observability for future consumers;
- prepares Engine extraction without performing it prematurely.

## Cost

The final release requires substantial non-feature engineering:

- CLI redesign;
- execution event instrumentation;
- cancellation handling;
- Rich integration;
- dependency audit;
- packaging;
- Chromium bundling;
- clean-environment testing;
- documentation;
- release engineering.

These costs are accepted as necessary for a stable `v1.0.0`.

---

# 75. Owner Approval

The owner explicitly approves:

- scope freeze;
- Rich;
- hybrid progress;
- two-level pipeline presentation;
- internal execution-observer architecture;
- distinct observed/extracted metrics;
- background browser as desired default subject to evidence;
- headed fallback if headless fails equivalence;
- rotating logs;
- portable ZIP;
- PyInstaller as primary candidate;
- `onedir` as preferred topology;
- bundled Chromium;
- unsigned release allowed;
- optional non-blocking SignPath investigation;
- SHA-256;
- graceful Ctrl+C cancellation;
- best-effort Windows console-close cleanup;
- post-v1 Engine extraction;
- post-v1 API/SaaS work.

**ADR-010 is therefore APPROVED.**

---

# 76. Pending Evidence-Gate Investigation

The following items are **not undecided product requirements**.

The decisions above already define the desired behavior.

These items require implementation evidence before the v1.0.0 release can be accepted.

## GATE R01 — Rich UX Prototype

Validate that Rich can provide:

- global progress;
- source-level progress;
- determinate tasks;
- indeterminate tasks;
- status messages;
- result summaries;
- tables;
- pagination interaction;

without polluting Engine/source code with presentation dependencies.

### Pass condition

Rich remains exclusively in CLI/presentation code and the prototype provides stable terminal rendering under representative workloads.

---

## GATE R02 — Execution Observer / Metrics Prototype

Validate the internal neutral event/callback design.

Determine the smallest safe internal contract needed to communicate:

- stage started;
- stage progress;
- stage completed;
- metrics update;
- issue/recoverable state;
- execution completion.

### Pass condition

Engine/source code emits neutral events and has no dependency on Rich or CLI presentation.

The existing `metrics_sink` is reconciled into or adapted to the new mechanism rather than duplicated.

---

## GATE R03 — Metrics Inventory

Audit every intended UX metric and classify it as:

```text
EXACT
DERIVED
UNAVAILABLE
```

At minimum evaluate:

- candidates observed;
- Businesses extracted;
- normalized;
- verified identities;
- unverified identities;
- duplicates suppressed;
- exportable/final count;
- recoverable issues;
- query time;
- stage times;
- batch time.

### Pass condition

Every displayed metric has one documented semantic meaning and a deterministic source.

No approximate value is presented as exact.

---

## GATE R04 — Headed vs Background Equivalence

Run controlled comparisons between:

- visible Chromium;
- background Chromium.

Evaluate:

- navigation;
- feed discovery;
- candidate counts;
- detail enrichment;
- P92 identity;
- Website Engine;
- normalization;
- timing;
- issues;
- cleanup.

### Preferred outcome

Background becomes v1.0.0 default.

### Accepted fallback

If equivalence is insufficient:

```text
Visible = default
Background = optional
```

This fallback does not by itself block release.

---

## GATE R05 — PyInstaller `onedir` Packaging Spike

Build the first representative portable package using:

```text
PyInstaller
onedir
Windows x64
```

Validate:

- executable startup;
- module discovery;
- Rich;
- openpyxl;
- Playwright;
- application resources;
- exports path;
- logs path;
- execution outside repo.

### Pass condition

The application runs without local Python/virtualenv dependency.

---

## GATE R06 — Chromium Bundle

Determine and validate the exact packaged Chromium layout required by the pinned Playwright version.

Evaluate:

- visible mode;
- background mode;
- browser lookup;
- executable portability;
- bundle size;
- startup behavior.

### Pass condition

The end user performs no separate browser installation.

---

## GATE R07 — Portable Relocation

Validate the packaged directory after:

- moving it;
- renaming its parent folder;
- copying to another supported path;
- running from a path containing spaces.

USB execution is desirable and should be evaluated when practical.

### Pass condition

Normal relocation does not depend on absolute developer paths.

---

## GATE R08 — Clean Windows Environment

Run the packaged artifact in a clean or isolated Windows 10/11 x64 environment without:

- repo;
- Python;
- virtualenv;
- Playwright developer installation.

Exercise:

- application launch;
- single query;
- batch query;
- browser visible;
- browser background where accepted;
- progress;
- results;
- CSV;
- XLSX;
- repeated operation;
- normal exit.

### Pass condition

Representative end-user workflows complete successfully.

---

## GATE R09 — Ctrl+C Graceful Cancellation

Validate cancellation during representative stages:

- navigation;
- feed discovery;
- detail enrichment;
- Website Engine;
- batch transition.

### Pass condition

The user gets confirmation when technically safe, cancellation performs cleanup, no corrupted export is retained and the process/application exits or returns to menu coherently.

No partial recovery is expected.

---

## GATE R10 — Windows Console-Close Behavior

Investigate actual packaged behavior for:

- console X;
- process termination events;
- shutdown/logout where practical.

### Pass condition

Best-effort cleanup is demonstrated and documented.

Interactive confirmation is not required for OS-enforced console termination.

---

## GATE R11 — Rotating Logs

Validate:

- local `logs/`;
- rotation;
- bounded disk usage;
- diagnostic usefulness;
- absence of unnecessary source/private data.

### Pass condition

Logs assist troubleshooting without becoming persistent telemetry or unlimited storage.

---

## GATE R12 — Export Directory

Validate `exports/` in the portable layout.

Test:

- CSV;
- XLSX;
- batch;
- repeated filenames;
- spaces in path;
- write failure;
- headers-only valid export;
- no incomplete artifact after failed write.

---

## GATE R13 — Dependency Audit

Audit `requirements.txt`.

Classify each dependency:

```text
runtime required
development-only
transitive
unused candidate
```

Do not remove dependencies without evidence.

### Pass condition

The shipped runtime set is understood and documented.

---

## GATE R14 — Third-Party Distribution Audit

Identify licensing/notices required for:

- Rich;
- PyInstaller runtime components where applicable;
- Playwright;
- Chromium;
- openpyxl;
- other shipped runtime dependencies.

### Pass condition

Required notices/licenses are included in the release package.

---

## GATE R15 — SignPath Feasibility

Optional investigation only.

Evaluate:

- eligibility;
- zero-cost status;
- application effort;
- signing workflow;
- release impact.

### Outcomes

```text
LOW FRICTION + FREE
-> may use SignPath

otherwise
-> release unsigned
```

Failure or abandonment of this gate SHALL NOT block `v1.0.0`.

SHA-256 remains mandatory either way.

---

## GATE R16 — Artifact Size / Startup

Measure representative:

- uncompressed portable size;
- ZIP size;
- cold startup;
- Chromium startup.

No arbitrary size target is defined.

### Pass condition

Size and startup are documented and judged operationally acceptable for a portable browser-based CLI.

---

## GATE R17 — Version Source

Evaluate a single source of truth for:

```text
v1.0.0
```

### Pass condition

CLI display, packaging metadata and release process cannot silently diverge in version number.

---

## GATE R18 — Contract Freeze Audit

Perform a final inventory of:

- Engine public contracts;
- CLI stable behavior;
- export schema;
- error semantics;
- limit policy;
- dedupe policy;
- filesystem/output behavior.

### Pass condition

No known breaking redesign remains pending before release.

---

## GATE R19 — Full Regression From Packaged State

Run the normal deterministic source regression and packaged smoke validation.

At minimum preserve all accepted `v0.9.x` invariants.

### Pass condition

No functional regression attributable to UX, instrumentation, packaging or hardening.

---

## GATE R20 — Release Candidate Acceptance

Produce an actual release candidate artifact:

```text
Prospector-CLI-v1.0.0-win64.zip
```

Perform final owner acceptance against the packaged artifact, not merely source code.

### Pass condition

Owner accepts:

- UX;
- execution;
- portability;
- progress;
- summaries;
- exports;
- error behavior;
- package structure;
- documentation.

Only after R20 passes may:

```text
v1.0.0 tag
GitHub Release
stable artifact publication
```

be performed.

---

# 77. Final ADR State

```text
ADR-010
APPROVED

PRODUCT SCOPE
FROZEN

FUNCTIONAL SCOPE
v0.9.x BASELINE

CLI UX
DECIDED

UI LIBRARY
RICH

PROGRESS MODEL
HYBRID

OBSERVABILITY
INTERNAL EVENT/CALLBACK CONTRACT

PACKAGING
WINDOWS x64 PORTABLE ZIP

PACKAGER
PYINSTALLER — PRIMARY CANDIDATE

TOPOLOGY
ONEDIR — PREFERRED

BROWSER
BUNDLED CHROMIUM

CODE SIGNING
OPTIONAL / NON-BLOCKING

SHA-256
REQUIRED

ENGINE EXTRACTION
POST-v1

API / SAAS
POST-v1

NEXT STEP
EVIDENCE GATES -> MASTER IMPLEMENTATION DESIGN -> RUNBOOK -> IMPLEMENTATION
```

## Owner amendment — 2026-10-08: portable browser capability

Status: APPROVED. This dated owner decision supersedes, for the Windows v1.0.0 portable distribution only, the earlier requirements in this ADR that the portable bundle support both Visible and Background, offer a browser-mode selector, or ship headed Chromium/Chrome for Testing. Those passages remain as decision history, not current portable requirements.

Reason: the redistribution basis for the exact Playwright 1.61.0 headed Chrome for Testing payload was not sufficiently demonstrated. This is a conservative shipping decision, not a conclusion that redistribution is unlawful.

The source/development CLI and Engine retain Background and Visible support. The Windows v1.0.0 portable is self-contained, supports Background only, defaults to Background, does not offer Visible, and must not contain the headed Chrome for Testing payload. The shared CLI applies this distribution capability without changing Engine, source, normalization, deduplication, or prospecting semantics.

For P106/R06, bundle only the browser assets needed for portable Background operation. R14 is **not** automatically passed by this decision: the exact remaining headless payload and its redistribution/notices must be audited and satisfied before P106 passes. P107 packaged smoke covers Background only; source/development Visible remains independently validated. R19 combines source regression with packaged-product smoke. R20 remains owner acceptance pending, and release publication remains unauthorized.

## Owner amendment — 2026-10-08: installed Microsoft Edge Stable

Status: APPROVED. This explicit owner decision supersedes for the Windows v1.0.0 portable the original bundled-Chromium requirement **and** the 2026-10-08 Background-only/bundled-headless amendment above. Both remain historical decisions and evidence, not current shipping requirements.

Reason: R14 did not establish a sufficient redistribution basis for the exact Playwright 1.61.0 Chrome for Testing headed or headless browser executable. Prospector therefore redistributes **no browser executable**. This is a distribution decision, not a change to prospecting or Engine business contracts.

Current v1.0.0 policy: Windows portable includes Prospector, Python, Playwright runtime and other application dependencies but requires **Microsoft Edge Stable installed externally**. Source/development and portable both offer Background and Visible via Playwright `chromium.launch(channel="msedge")`; Background is the desired default subject to a repeated Edge-specific R04. Prospector does not install Edge, invoke `playwright install msedge`, use arbitrary `executable_path`, or bypass enterprise policies. An unavailable or blocked Edge launch must produce an actionable CLI error and technical log without a normal-user traceback.

P106/R06 is now **Browser Runtime Availability**, not Chromium Bundle: both modes, controlled absence/failure, no browser bundle/cache/installer dependency. R14 audits only software actually shipped; Edge redistribution is NOT APPLICABLE, while Python/application dependency notices remain mandatory. P107 must prove relocation, clean/isolated Windows execution with installed Edge, packaged live smoke and cleanup; P108 prepares the RC and leaves R20 to the owner. No browser redistribution, Playwright downgrade, push, tag, release or A3 operation is authorized.

## Owner release-policy exception — 2026-10-08: R08 clean-machine waiver

For the initial v1.0.0 release only, the owner explicitly waives pre-release validation on a separate clean/isolated Windows machine. R08 is **OWNER_WAIVED / DEFERRED_POST_RELEASE**, never PASS. The original clean-machine requirement remains good engineering practice and is preserved above as historical policy. No second machine is available and Windows Sandbox is unavailable on the current host. Relocated portable execution without a Playwright-managed browser cache has been exercised, with installed Microsoft Edge Stable as an external prerequisite; this is not clean-machine evidence. The owner accepts possible environment-specific Windows/Edge/enterprise-policy packaging defects, to be addressed after release as maintenance/hardening (normally v1.0.1/v1.0.2 unless later policy differs).

For this release R19 means source regression plus packaged-product smoke on the current host; it does not imply an external-machine test. R09 controlled cancellation and R10 best-effort console-close cleanup remain required. P107/P108 may proceed with R08 waived. R20 remains owner acceptance pending; A3 publication is not authorized.

**END ADR-010**

# Prospector CLI — v1.0.0 Master Implementation Design

**Status:** ACCEPTED — AUTHORITATIVE PROJECT AUTHORITY  
**Target:** Prospector CLI `v1.0.0`  
**Document type:** Master Implementation Design  
**Authority:** `ADR-010 — Stable CLI UX, Windows Portable Distribution and v1.0.0 Release Freeze`  
**ADR status:** `APPROVED`  
**Predecessor:** `v0.9.x — OWNER ACCEPTED / COMPLETE`  
**Accepted functional implementation baseline:** `c7193d55a36618e934e29a9678b3f9b01e9b6543`  
**v0.9.x documentation closure / proposed v1.0.0 starting repository state:** `71cb7f8981281ce68a2e9936ba01554e69e8c7ed`

---

# 1. Purpose

This Master defines how Prospector CLI shall move from the accepted `v0.9.x` implementation to the first stable `v1.0.0` release.

It translates ADR-010 into an ordered implementation sequence.

This document does not expand functional prospecting scope.

It defines:

- implementation boundaries;
- patch sequence;
- internal contracts;
- evidence gates;
- validation order;
- release blockers;
- STOP conditions;
- final freeze sequence.

The objective is:

```text
v0.9.x accepted functionality
        |
        v
v1.0.0 hardening
        |
        v
formal CLI UX
        |
        v
execution observability
        |
        v
graceful cancellation / logging
        |
        v
portable Windows packaging
        |
        v
clean-machine evidence
        |
        v
contract freeze
        |
        v
release candidate
        |
        v
v1.0.0 stable release
```

---

# 2. Normative Authority Order

Implementation SHALL follow this authority order:

```text
1. ADR-010
2. this Master Implementation Design
3. future v1.0.0 Autonomous Implementation Runbook
4. accepted v0.9.x contracts
5. existing source/tests/documentation
```

If a lower-level artifact conflicts with ADR-010, ADR-010 wins.

If implementation requires a decision not covered by ADR-010 or this Master:

`STOP / OWNER REVIEW`

No implementation convenience may silently create a new business rule.

---

# 3. Functional Freeze

The accepted `v0.9.x` behavior remains authoritative.

The following SHALL NOT be redesigned during `v1.0.0`:

- `ProspectorEngine.search()`;
- `ProspectorEngine.search_many()`;
- current Google Maps extraction semantics;
- current Website Engine enrichment semantics;
- normalization;
- source identity semantics;
- verified-only interquery deduplication;
- sequential execution;
- current limit policy;
- SearchResult semantics;
- BatchSearchResult semantics;
- seven-column export contract;
- existing partial/failure semantics.

`v1.0.0` may add supporting internal infrastructure required by ADR-010.

That infrastructure SHALL NOT constitute new prospecting functionality.

---

# 4. v1.0.0 Primary Workstreams

Implementation is divided into four architectural workstreams:

```text
A. FINAL HARDENING
   lifecycle
   cleanup
   filesystems
   dependency audit
   logging
   cancellation
   regression

B. FINAL CLI UX
   Rich
   navigation
   confirmation
   progress
   observability
   metrics
   summaries
   pagination

C. WINDOWS PORTABLE DISTRIBUTION
   PyInstaller
   onedir
   bundled Chromium
   relocation
   clean environment
   artifact validation

D. RELEASE FREEZE
   contract audit
   documentation
   version source
   checksums
   RC
   tag
   GitHub Release
```

The patch sequence below intentionally crosses these workstreams where dependencies require it.

---

# 5. Patch Sequence

The v1.0.0 implementation line SHALL use the following logical patches:

```text
P101 — Baseline Audit and Release Foundations
P102 — Execution Observability and Metrics
P103 — Final Rich CLI UX
P104 — Cancellation, Logging and Filesystem Hardening
P105 — Browser Mode Validation and Runtime Stabilization
P106 — Windows Portable Packaging
P107 — Clean-Machine and Packaged Regression
P108 — Contract Freeze, Release Candidate and Release Closure
```

The numbering is logical documentation sequencing.

Actual Git commit count does not need to equal eight.

---

# 6. P101 — Baseline Audit and Release Foundations

## Objective

Establish the exact v1.0.0 starting state and remove ambiguity before functional hardening begins.

## Scope

Audit:

- current repository structure;
- public Engine contracts;
- CLI entrypoints;
- ExportService;
- logging;
- filesystem assumptions;
- dependency inventory;
- version representation;
- browser/runtime assumptions;
- existing metrics instrumentation;
- current tests;
- packaging-sensitive imports/resources.

## Required baseline

Starting repository state SHALL correspond to:

```text
71cb7f8981281ce68a2e9936ba01554e69e8c7ed
```

unless a later owner-approved documentation-only commit exists before implementation starts.

Functional baseline remains:

```text
c7193d55a36618e934e29a9678b3f9b01e9b6543
```

## Deliverables

Create/update planning evidence for:

```text
temp/Planeacion/v1.0.0/
```

Recommended initial documents:

```text
AuthorityBaseline.md
CurrentStateAudit.md
DependencyInventory.md
ContractInventory.md
MetricsInventory.md
PackagingAssumptions.md
ValidationMatrix.md
ImplementationProgress.md
ImplementationBlockers.md
EvidenceIndex.md
```

## Dependency inventory

Every current dependency SHALL initially be classified as:

```text
DIRECT_RUNTIME
TRANSITIVE_RUNTIME
DEVELOPMENT_TEST
BUILD_ONLY
UNUSED_CANDIDATE
UNKNOWN
```

No dependency SHALL be removed merely because it appears unused.

Removal requires evidence and full regression.

## Rich

Rich is already owner-approved by ADR-010.

It is not a discretionary dependency.

Its exact pinned version shall be selected during implementation compatibility validation.

## PyInstaller

PyInstaller SHALL be treated as build tooling, not a prospecting runtime capability.

Prefer isolating build dependencies from user runtime dependencies.

## Version source

P101 SHALL identify or establish one controlled source of product version.

The final value is:

```text
1.0.0
```

The implementation SHALL prevent independent CLI/package/release version strings from silently diverging.

Exact module/file location is an implementation decision.

## Evidence gates addressed

```text
R13 — Dependency Audit
R17 — Version Source
R18 — Contract Freeze Audit (initial inventory only)
```

## Exit criteria

P101 passes when:

- baseline is clean and known;
- current tests pass;
- contracts are inventoried;
- dependencies are classified;
- existing metrics instrumentation is inventoried;
- release-sensitive filesystem assumptions are known;
- version-source strategy is documented;
- no hidden scope expansion is identified.

---

# 7. P102 — Execution Observability and Metrics

## Objective

Create neutral internal execution observability that can drive the final CLI without coupling Engine/source code to Rich.

## Architectural rule

The data path SHALL be:

```text
Engine / source pipeline
        |
        v
neutral execution events
        |
        v
internal observer
        |
        +------> CLI Rich renderer
        |
        +------> future consumer adapter
```

Rich SHALL NOT cross the CLI boundary.

## Internal status

The observability contract is:

```text
INTERNAL INFRASTRUCTURE
NOT PUBLIC v1.0.0 ENGINE API
```

It SHALL NOT be added to the stable public Engine freeze.

## Conceptual model

Implementation may use names such as:

```text
ExecutionEvent
ExecutionStage
ExecutionMetrics
ExecutionObserver
ExecutionSummary
```

These names are not normative.

The semantics are.

## Minimum event semantics

The internal mechanism SHALL be able to communicate at least:

```text
execution_started
stage_started
progress_updated
metric_updated
stage_completed
recoverable_issue_observed
execution_completed
execution_failed
execution_cancelled
```

Exact event granularity SHALL avoid excessive event traffic.

## No-op path

Execution without an observer SHALL remain valid.

The existing programmatic Engine paths SHALL not require a presentation consumer.

## Existing metrics_sink

The existing Google Maps `metrics_sink` SHALL be:

- adapted;
- migrated;
- wrapped;

or otherwise reconciled into the new observability mechanism.

A second unrelated metrics system SHALL NOT be created.

## Metrics required

At minimum the implementation SHALL establish semantic ownership for:

```text
requested_limit
maps_candidates_observed
businesses_extracted
businesses_normalized
verified_identities
unverified_identities
duplicates_suppressed
exportable_businesses
recoverable_issue_count
query_execution_seconds
batch_execution_seconds
navigation_seconds
feed_seconds
detail_seconds
website_seconds
```

Additional metrics require actual usefulness.

## Exact / derived / unavailable

Each metric SHALL be classified:

```text
EXACT
DERIVED
UNAVAILABLE
```

Only EXACT or well-defined DERIVED values may be shown as numeric user metrics.

## Candidates vs Businesses

The implementation SHALL maintain the ADR distinction:

```text
Maps candidates observed
!=
Businesses extracted
```

No generic ambiguous `results_found` metric shall replace them.

## Stage timing

Timing SHALL use monotonic execution measurement suitable for elapsed durations.

No wall-clock timestamp is required for UX metrics unless logging needs it.

## Normalization

The global normalization stage SHALL expose observability without changing normalization behavior.

It SHALL still occur exactly once per query.

## Deduplication

Batch selection SHALL expose suppression metrics without moving deduplication decisions into CLI code.

## Evidence gates addressed

```text
R02 — Execution Observer / Metrics Prototype
R03 — Metrics Inventory
```

## Tests

Add deterministic tests for:

- no-op observer;
- event order where contractually important;
- metric semantic ownership;
- single search;
- batch search;
- controlled failure;
- recoverable issues;
- no Rich import in Engine/source;
- existing results unchanged with observer enabled/disabled.

Do not over-test cosmetic event frequency.

## Exit criteria

P102 passes when:

- neutral observer mechanism exists;
- existing metrics are reconciled;
- single and batch behavior remain unchanged;
- every displayed metric has defined semantics;
- Engine/source do not depend on Rich;
- full offline regression remains green.

---

# 8. P103 — Final Rich CLI UX

## Objective

Replace the development-oriented CLI presentation with the stable v1.0.0 user experience.

## Main menu

The CLI SHALL expose conceptually:

```text
Prospector CLI
v1.0.0

1. New Search
2. Multiple Searches
3. Exit
```

Exact Rich styling is not contractually frozen.

## Application loop

The CLI SHALL remain active until:

- explicit Exit;
- fatal unrecoverable application condition;
- operating-system termination.

Successful operations return to interactive control.

## Single search workflow

Required flow:

```text
Main Menu
  -> New Search
  -> Capture inputs
  -> Review
  -> Edit / Back / Confirm
  -> Browser Mode
  -> Effective Configuration
  -> Execute
  -> Live Progress
  -> Summary
  -> View / Export / Back
```

## Multiple search workflow

Required flow:

```text
Main Menu
  -> Multiple Searches
  -> Query 1
  -> Query 2
  -> optional Query 3
  -> Review
  -> Edit / Back / Confirm
  -> Browser Mode
  -> Effective Configuration
  -> Execute sequentially
  -> Live Progress
  -> Per-query summaries
  -> Batch Summary
  -> View / Export / Back
```

## CLI query limits

Interactive CLI remains:

```text
2–3 queries
```

Programmatic Engine remains:

```text
1–5 queries
```

Do not conflate these boundaries.

## Confirmation

Both single and batch require confirmation before source execution.

Rejecting confirmation means inputs remain editable.

After source execution begins, inputs become immutable for that execution.

## Effective configuration

The CLI SHALL display at least:

```text
source
keyword
location
limit
website enrichment = enabled
browser mode
batch query count when applicable
```

## Browser mode choice

After input confirmation and before `BrowserRuntime` creation:

```text
1. Background
2. Visible
```

Desired default:

```text
Background
```

subject to P105 evidence.

## Website enrichment

Website enrichment remains enabled and is not exposed as an end-user toggle.

## Rich progress presentation

The final CLI SHALL support:

- global execution state;
- source internal state;
- determinate progress;
- indeterminate progress;
- elapsed time;
- useful metric updates.

Conceptual example:

```text
Prospector CLI v1.0.0

Search 2 / 3
Global pipeline
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Google Maps

Navigation             Complete
Feed discovery          64 candidates observed
Detail enrichment       31 / 50
Website enrichment      24 / 50
Normalization           Pending
Deduplication           Pending

Elapsed                 02:14
```

This is illustrative, not a styling contract.

## No fake progress

The CLI SHALL NOT display a percentage when no meaningful denominator exists.

## User-facing statuses

At minimum presentation must distinguish:

```text
SUCCESS
SUCCESS WITH ISSUES
PARTIAL
FAILED
BATCH INTERRUPTED
CANCELLED
```

## Summary

Every query gets a summary.

Batch gets an additional consolidated summary.

Example semantic content:

```text
Requested limit
Maps candidates observed
Businesses extracted
Businesses normalized
Verified identity count
Unverified identity count
Duplicates suppressed
Final exportable
Recoverable issues
Execution time
```

Only metrics that actually apply shall be shown.

## Result navigation

Initial post-execution surface is Summary.

Then:

```text
1. View Results
2. Export Results
3. Back
```

## Pagination

`View Results` SHALL show:

```text
10 Businesses per page
```

Navigation SHALL avoid dumping the complete result set into the terminal.

## Post-export

After successful export, ask whether to:

```text
Run another search
Return to main menu
```

## Technical noise

Normal user view SHALL NOT contain:

- raw stack traces;
- internal selectors;
- browser object information;
- low-level debug output.

Those belong in logs.

## Evidence gates addressed

```text
R01 — Rich UX Prototype
```

## Tests

Add deterministic presentation-flow tests around semantic behavior:

- menu navigation;
- back/edit;
- confirmation;
- effective config;
- result menu;
- 10-item pagination;
- repeated searches;
- batch flow;
- recoverable issue summary.

Avoid brittle tests on ANSI colors or exact terminal spacing unless intentionally frozen.

## Exit criteria

P103 passes when:

- Rich owns presentation only;
- UX matches ADR-010;
- application supports repeated searches;
- no result flood occurs;
- summary/pagination/export flow works;
- existing Engine semantics remain intact.

---

# 9. P104 — Cancellation, Logging and Filesystem Hardening

## Objective

Make long-running CLI execution safe and operationally understandable.

---

# 9.1 Controlled Ctrl+C Cancellation

During active execution:

```text
Ctrl+C
```

SHALL request cancellation rather than immediately kill the process.

The CLI SHALL ask for confirmation when technically safe.

Conceptually:

```text
Cancel current execution?

All unexported results from this execution will be lost.

[y/N]
```

## No response

If No:

- execution continues.

## Yes response

If Yes:

- execution cancellation begins;
- BrowserRuntime cleanup is attempted;
- incomplete unexported work is discarded;
- no checkpoint is created;
- no resume data is created.

## No partial persistence

Cancellation SHALL NOT produce a partial recovery system.

If work has not already been exported through a completed export action, cancellation may lose it.

---

# 9.2 Cancellation Architecture

Cancellation SHALL not be implemented through arbitrary process termination if a safe cooperative mechanism is feasible.

The implementation SHALL investigate the smallest mechanism compatible with the current synchronous pipeline.

It may use:

- internal cancellation signal;
- cancellation token;
- observer/control signal;

or equivalent.

The mechanism SHALL NOT create:

- background workers;
- queues;
- multithreaded batch orchestration;
- async job infrastructure.

---

# 9.3 Runtime Cleanup

Cancellation SHALL preserve the existing BrowserRuntime ownership model.

Pages/browser/Playwright cleanup remain owned by BrowserRuntime and related established resource owners.

---

# 9.4 Windows Console Close

Console window X / logout / OS termination receives:

```text
BEST-EFFORT CLEANUP
```

Interactive confirmation SHALL NOT be guaranteed.

No false promise of recoverability is allowed.

---

# 9.5 Logging

Portable distribution SHALL use:

```text
logs/
```

User output and diagnostics SHALL be separate.

Use bounded rotation.

Conceptually:

```text
prospector.log
prospector.log.1
prospector.log.2
```

Exact count and size are implementation details.

## Logging restrictions

Do not unnecessarily persist:

- entire page HTML;
- browser storage;
- arbitrary URL dumps;
- secrets;
- full exported prospect datasets.

Logging should primarily support:

- stage transitions;
- errors;
- cleanup;
- build/version information;
- diagnostic timings.

---

# 9.6 Export filesystem

Default user exports SHALL live under:

```text
exports/
```

relative to the portable application root.

Filesystem handling SHALL work independently of current working directory where practical.

## Path resolver

A centralized application-path strategy SHOULD determine:

```text
application root
exports path
logs path
packaged resource path
```

Avoid duplicated path derivation across modules.

---

# 9.7 Export safety

Preserve existing behavior:

- independent query files;
- unique names;
- no silent overwrite;
- headers-only valid outputs;
- FAILED query no export;
- partial write cleanup.

Packaged execution must not regress these guarantees.

---

# 9.8 Evidence gates addressed

```text
R09 — Ctrl+C Graceful Cancellation
R10 — Windows Console-Close Behavior
R11 — Rotating Logs
R12 — Export Directory
```

## Exit criteria

P104 passes when:

- Ctrl+C behavior is deterministic;
- cleanup is reliable;
- no checkpoint/resume exists;
- console close is documented as best-effort;
- logs rotate;
- exports resolve from portable app structure;
- no hardcoded developer path remains in these flows.

---

# 10. P105 — Browser Mode Validation and Runtime Stabilization

## Objective

Determine the stable v1.0.0 default browser mode with real evidence.

## Modes

Compare:

```text
VISIBLE / HEADED

BACKGROUND / HEADLESS
```

## Required comparison

Evaluate the same or controlled-equivalent queries for:

- navigation success;
- feed behavior;
- candidate counts;
- extracted Businesses;
- detail enrichment;
- verified P92 identities;
- unverified identities;
- Website Engine behavior;
- SearchIssues;
- normalization;
- timing;
- cleanup.

## Desired decision

If equivalent enough for accepted product behavior:

```text
Background = default
Visible = optional
```

## Approved fallback

If background behavior is materially less reliable:

```text
Visible = default
Background = optional where supported
```

This fallback is owner-approved by ADR-010 and does not itself block release.

## No silent semantic difference

If browser mode changes actual Engine semantics or causes unexplained systematic data loss:

`STOP / OWNER REVIEW`

until understood.

## Gate authorization

This patch requires live external Google Maps validation.

The eventual implementation Runbook SHALL explicitly identify this as an owner-authorized live evidence phase.

It SHALL NOT run automatically as part of offline regression.

## Evidence gates addressed

```text
R04 — Headed vs Background Equivalence
```

## Exit criteria

P105 passes when:

- browser-mode behavior is measured;
- stable default is selected using ADR policy;
- choice is documented;
- normal CLI exposes both modes where safe.

---

# 11. P106 — Windows Portable Packaging

## Objective

Produce the first representative self-contained Windows x64 artifact.

## Primary tooling

Use:

```text
PyInstaller
```

Primary topology:

```text
onedir
```

## Primary artifact structure

Conceptually:

```text
Prospector-CLI-v1.0.0-win64/
├── prospector.exe
├── packaged runtime
├── Chromium/browser assets
├── exports/
├── logs/
├── LICENSE
├── third-party notices
└── user documentation
```

Actual PyInstaller internal directories may differ.

## Chromium

The packaged artifact SHALL include the browser binaries required by the pinned Playwright release.

The user SHALL NOT need:

```text
playwright install
```

## Visible + background

The bundle SHALL contain sufficient runtime/browser resources to support both approved modes.

## Browser lookup

The packaged app SHALL find its Chromium assets without relying on:

- developer home cache;
- repository-specific paths;
- existing Playwright installation.

## PyInstaller onefile

`onefile` MAY be tested as secondary evidence.

It SHALL NOT replace `onedir` unless it is demonstrated to be at least as reliable and operationally simpler.

No requirement exists to produce a physically single file.

## Portable relocation

Test the built directory after:

- copying it;
- moving it;
- changing parent directory;
- paths containing spaces;
- non-repository location.

USB execution is desirable evidence but not a release blocker.

## Artifact size

Measure:

```text
uncompressed distribution size
ZIP size
application cold startup
Chromium startup
```

No arbitrary pass/fail size threshold is defined.

The measurements SHALL be documented.

## Dependency inclusion

Use P101 dependency audit to avoid accidentally shipping unrelated development tooling.

## Third-party notices

Before RC, determine notices/licenses required for shipped components.

## SignPath

Evaluate only if:

- free;
- project qualifies;
- low effort;
- no release delay.

Paid signing is prohibited for this release.

Unsigned artifact is acceptable.

## Evidence gates addressed

```text
R05 — PyInstaller onedir Packaging Spike
R06 — Chromium Bundle
R07 — Portable Relocation
R14 — Third-Party Distribution Audit
R15 — SignPath Feasibility
R16 — Artifact Size / Startup
```

## Exit criteria

P106 passes when:

- portable artifact builds reproducibly enough for RC;
- no Python installation is required;
- Chromium is bundled;
- application starts outside repository;
- normal relocations work;
- licensing requirements are known;
- artifact size/startup are documented.

---

# 12. P107 — Clean-Machine and Packaged Regression

## Objective

Validate the product that users will actually receive, not only source execution.

## Clean environment

Use a clean or isolated:

```text
Windows 10/11 x64
```

environment without:

- repository checkout;
- developer virtualenv;
- system dependency on project Python environment;
- Playwright developer installation.

## Required packaged smoke

At minimum validate:

```text
launch
main menu
single search
batch search
background mode if accepted
visible mode
live progress
summary
result pagination
CSV export
XLSX export
repeated search
normal exit
Ctrl+C cancellation
```

## Filesystem cases

Validate:

- writable normal path;
- path with spaces;
- moved portable directory;
- non-admin account;
- logs rotation;
- exports directory;
- repeated exports;
- export error behavior.

## Packaged regression

The source test suite remains required.

Additionally, packaged smoke SHALL prove that freezing/packaging has not broken:

- imports;
- resources;
- Playwright;
- Chromium lookup;
- Rich rendering;
- openpyxl/XLSX;
- path handling.

## Live scope

Packaged Google Maps validation is external/live and SHALL be explicitly authorized in the future Runbook.

Offline source tests do not substitute for packaged live evidence.

## Evidence gates addressed

```text
R08 — Clean Windows Environment
R19 — Full Regression From Packaged State
```

## Exit criteria

P107 passes when:

- clean-machine workflows succeed;
- source regression remains green;
- packaged artifact behaves as expected;
- no repository/Python environment dependency exists.

---

# 13. P108 — Contract Freeze, Release Candidate and Release Closure

## Objective

Freeze the first stable product and create the final release candidate.

---

# 13.1 Public Engine Contract Audit

Review:

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

Objective:

```text
CONFIRM / FREEZE
```

not redesign.

The internal observability contract remains excluded.

---

# 13.2 CLI Contract Freeze

Freeze:

- main navigation;
- single-search workflow;
- batch workflow;
- confirmations;
- limits;
- browser-mode choice;
- summary semantics;
- pagination = 10;
- cancellation semantics;
- export formats/schema;
- default output directories.

Cosmetic Rich styling is not semantic API.

---

# 13.3 Documentation

Complete user documentation for:

- installation/extraction;
- launch;
- system requirements;
- browser modes;
- searches;
- limits;
- progress;
- metrics;
- summaries;
- pagination;
- exports;
- logs;
- cancellation;
- known limitations;
- verified-identity dedupe;
- troubleshooting;
- license.

Developer docs SHALL cover:

- source setup;
- testing;
- packaging;
- architecture;
- release procedure;
- contract boundaries.

---

# 13.4 Release candidate

Produce:

```text
Prospector-CLI-v1.0.0-win64.zip
```

as the actual RC artifact.

The owner SHALL evaluate the artifact, not merely source code.

---

# 13.5 SHA-256

Generate and record SHA-256 for the final candidate/release artifact.

---

# 13.6 Owner acceptance

Owner acceptance SHALL evaluate:

```text
UX
execution
progress
metrics
summaries
pagination
cancellation
exports
browser modes
portability
package layout
documentation
known limitations
```

## Evidence gates addressed

```text
R17 — Version Source (final confirmation)
R18 — Contract Freeze Audit
R20 — Release Candidate Acceptance
```

---

# 13.7 Release operations

Only after R20 passes may release operations occur:

```text
final release commit
tag v1.0.0
GitHub Release v1.0.0
upload Windows artifact
publish SHA-256
publish release notes
```

These GitHub operations require explicit authorization in the eventual Runbook/owner activation.

Master approval alone SHALL NOT authorize release publication.

---

# 13.8 Final state

Successful P108 produces:

```text
Prospector CLI v1.0.0
OWNER ACCEPTED
STABLE
TAGGED
RELEASED
CONTRACTS FROZEN
WINDOWS PORTABLE ARTIFACT PUBLISHED
```

Afterward:

```text
CLI -> MAINTENANCE MODE
```

---

# 14. Evidence Gate Mapping

| Gate | Patch | Requirement |
|---|---|---|
| R01 | P103 | Rich UX prototype |
| R02 | P102 | Observer/metrics prototype |
| R03 | P102 | Metrics inventory |
| R04 | P105 | Headed/background equivalence |
| R05 | P106 | PyInstaller `onedir` |
| R06 | P106 | Chromium bundle |
| R07 | P106 | Portable relocation |
| R08 | P107 | Clean Windows environment |
| R09 | P104 | Ctrl+C cancellation |
| R10 | P104 | Windows console close |
| R11 | P104 | Rotating logs |
| R12 | P104 | Export directory |
| R13 | P101 | Dependency audit |
| R14 | P106 | Third-party notices |
| R15 | P106 | SignPath optional feasibility |
| R16 | P106 | Artifact size/startup |
| R17 | P101 + P108 | Version source |
| R18 | P101 + P108 | Contract freeze |
| R19 | P107 | Packaged/full regression |
| R20 | P108 | Release candidate acceptance |

---

# 15. Patch Dependencies

Required order:

```text
P101
  |
  v
P102
  |
  v
P103
  |
  v
P104
  |
  +----------+
  |          |
  v          v
P105       groundwork for P106
  |          |
  +----+-----+
       |
       v
     P106
       |
       v
     P107
       |
       v
     P108
```

P105 and early packaging investigation may technically overlap after P104, but final P106 packaging decisions must use the accepted browser-mode outcome.

No final release candidate may precede P107.

---

# 16. Validation Layers

The v1.0.0 line SHALL use four evidence classes.

## L1 — deterministic unit

No public network.

Validate:

- event models;
- observer behavior;
- metrics;
- CLI navigation;
- pagination;
- configuration;
- cancellation control logic;
- path resolution;
- logging configuration.

## L2 — controlled integration

No Google Maps public dependency unless explicitly marked.

Validate:

- Engine + observer;
- normalization;
- batch;
- ExportService;
- filesystem;
- Rich semantic flow where practical;
- BrowserRuntime using controlled resources where existing suite supports it.

## L3 — live source evidence

Explicitly authorized.

Validate:

- Google Maps;
- headed/headless;
- identity;
- Website Engine;
- real timings;
- cancellation where safe.

## L4 — packaged clean-machine evidence

Explicitly authorized.

Validate actual distributed artifact.

---

# 17. Regression Baseline

At the start of v1.0.0 implementation, reproduce the accepted deterministic baseline.

Historical accepted v0.9.x evidence:

```text
unit          194 PASS
integration    68 PASS
full          262 PASS
live E2E        1 deselected
```

Exact test counts MAY increase as v1.0.0 adds tests.

Success criterion is not preserving the numerical count.

Success criterion is preserving all accepted behavior while new tests pass.

---

# 18. Test Policy

New tests SHALL prioritize semantic behavior.

Avoid tests tied to:

- ANSI escape sequences;
- exact Rich color values;
- decorative borders;
- exact whitespace;

unless a formatting detail is intentionally contractually significant.

Test:

```text
what the user can do
what the Engine emits
what metrics mean
what files are created
what cleanup occurs
```

rather than purely visual snapshots.

---

# 19. Release Blockers

The following are blocking:

```text
accepted v0.9.x regression

new business-rule change without authorization

Rich dependency leaking into Engine/source

observer changing result semantics

fake/ambiguous user metrics

unreliable BrowserRuntime cleanup

Ctrl+C leaving unsafe runtime state

portable build requiring Python

portable build requiring manual Playwright setup

Chromium not found from packaged artifact

hardcoded repository/developer path

broken CSV/XLSX behavior

unbounded logs

clean-machine failure

unknown mandatory third-party licensing obligations

public contract known to require breaking redesign

RC rejected by owner
```

---

# 20. Non-Blocking Outcomes

The following SHALL NOT independently block release:

```text
single-file .exe unavailable

installer unavailable

SignPath unavailable

release unsigned

USB execution unsupported on some systems

background/headless rejected as default
```

Provided the ADR-approved fallback behavior is satisfied.

---

# 21. STOP / OWNER REVIEW Conditions

Codex/implementation SHALL STOP when any of the following occurs:

1. a v0.9.x accepted contract must change;
2. a new prospecting capability appears necessary;
3. a business-policy choice is required;
4. normalization semantics would change;
5. verified-identity dedupe semantics would change;
6. Website enrichment behavior must be materially redefined;
7. public Engine contract requires breaking redesign;
8. observer would need to become public API contrary to ADR;
9. progress requires fake metrics;
10. cancellation requires job/queue/concurrency architecture;
11. BrowserRuntime ownership must be fundamentally redesigned;
12. Rich must enter Engine/source code;
13. packaging requires an unapproved proprietary/paid dependency;
14. code signing requires payment;
15. PyInstaller proves unsuitable and replacement packager is needed;
16. Chromium licensing/distribution presents an unresolved blocker;
17. headless/visible behavior exposes unexplained semantic divergence;
18. portable package needs administrator installation contrary to ADR;
19. clean-machine execution requires undeclared prerequisites;
20. unexpected Git state or unrelated concurrent changes appear;
21. live Internet execution is required without authorization;
22. Git branch/commit/push/tag/release operation exceeds current authorization.

---

# 22. Git and Release Safety

The future Runbook SHALL separately control permission for:

- branch creation/change;
- commit;
- push;
- tag;
- GitHub Release;
- artifact upload.

This Master defines the target operations.

It does not itself authorize them.

No destructive Git cleanup commands shall be used as routine implementation operations.

---

# 23. Proposed Development Branch

Recommended implementation branch:

```text
v1.0.0
```

created from the accepted v0.9.x closure state.

Branch creation requires owner authorization in the future implementation activation.

---

# 24. Documentation Structure

Recommended local planning folder:

```text
temp/Planeacion/v1.0.0/
```

Recommended contents as implementation progresses:

```text
ADR-010-Stable-CLI-UX-Windows-Portable-Distribution-and-Release-Freeze.md
V1-0-0-Master-Implementation-Design.md
V1-0-0-Autonomous-Implementation-Runbook.md
AuthorityBaseline.md
CurrentStateAudit.md
DependencyInventory.md
ContractInventory.md
MetricsInventory.md
PackagingAssumptions.md
ImplementationProgress.md
ImplementationBlockers.md
ValidationMatrix.md
AuditDiff.md
EvidenceIndex.md
PackagingEvidence.md
CleanMachineEvidence.md
ReleaseCandidateReport.md
OwnerAcceptanceChecklist.md
V1-0-0-Owner-Acceptance-Closure.md
FinalReleaseReport.md
```

Not all documents need to exist before implementation starts.

---

# 25. Proposed Validation Matrix State Before Implementation

Initially:

```text
R01 PENDING
R02 PENDING
R03 PENDING
R04 PENDING
R05 PENDING
R06 PENDING
R07 PENDING
R08 PENDING
R09 PENDING
R10 PENDING
R11 PENDING
R12 PENDING
R13 PENDING
R14 PENDING
R15 OPTIONAL / PENDING
R16 PENDING
R17 PENDING
R18 PENDING
R19 PENDING
R20 PENDING
```

R15 failure does not imply overall failure if unsigned-release requirements are satisfied.

---

# 26. Proposed Implementation State Machine

```text
MASTER ACCEPTED
      |
      v
OWNER IMPLEMENTATION AUTHORIZATION
      |
      v
RUNBOOK CREATED
      |
      v
RUNBOOK APPROVED
      |
      v
P101
      |
      v
P102
      |
      v
P103
      |
      v
P104
      |
      v
P105
      |
      v
P106
      |
      v
P107
      |
      v
P108
      |
      v
OWNER RC ACCEPTANCE
      |
      v
RELEASE AUTHORIZATION
      |
      v
TAG + GITHUB RELEASE
      |
      v
v1.0.0 CLOSED
```

---

# 27. Completion Definition

`v1.0.0` is not complete merely because source code compiles.

It is complete only when:

```text
functional regression      PASS
formal CLI UX              PASS
observer/metrics           PASS
graceful cancellation      PASS
logging/filesystem         PASS
browser-mode policy        PASS
portable packaging         PASS
bundled Chromium           PASS
portable relocation        PASS
clean Windows execution    PASS
third-party audit          PASS
contract freeze            PASS
packaged regression        PASS
owner RC acceptance        PASS
release documentation      PASS
SHA-256                    GENERATED
tag                         PUBLISHED
GitHub Release              PUBLISHED
stable artifact             PUBLISHED
```

---

# 28. Post-Release Freeze

After release:

```text
Prospector CLI v1.0.0
```

becomes the first frozen stable reference implementation.

Subsequent CLI changes require either:

- bugfix maintenance;
- explicit future CLI version planning.

Architectural expansion proceeds separately toward:

```text
Prospector Engine extraction
        |
        +--> CLI consumer
        +--> API consumer
        +--> future multitenant system
```

The extraction project SHALL use the stable v1.0.0 contracts as its starting reference.

---

# 29. Master Decision Summary

```text
VERSION
v1.0.0

FUNCTIONAL BASELINE
v0.9.x OWNER ACCEPTED

NEW PROSPECTING FEATURES
NONE

PATCHES
P101–P108

UI
Rich

OBSERVABILITY
internal neutral observer/events

METRICS
ephemeral UX metrics

CANCELLATION
confirmed Ctrl+C + graceful cleanup

LOGGING
rotating local logs

EXPORT ROOT
portable exports/

BROWSER
visible + background

TARGET DEFAULT
background subject to R04

PACKAGING
PyInstaller onedir

DISTRIBUTION
Windows 10/11 x64 portable ZIP

CHROMIUM
bundled

INSTALLER
optional

SINGLE EXE
optional

SIGNING
optional free SignPath only / unsigned allowed

CHECKSUM
SHA-256 required

CLEAN MACHINE
required

PUBLIC CONTRACT FREEZE
required

OWNER RC ACCEPTANCE
required

TAG / RELEASE
only after R20

POST-v1
Engine extraction + future API
```

---

# 30. Master Status

Current state:

```text
ADR-010
APPROVED — AUTHORITATIVE PROJECT AUTHORITY

V1-0-0 MASTER IMPLEMENTATION DESIGN
ACCEPTED — AUTHORITATIVE PROJECT AUTHORITY

IMPLEMENTATION
AUTHORIZED BY THIS DOCUMENT

NEXT
RUNBOOK CREATION -> RUNBOOK APPROVAL -> IMPLEMENTATION
```

## Owner amendment — 2026-10-08: Background-only Windows portable

Status: ACCEPTED under the explicit owner decision. Earlier passages requiring both browser modes in the portable, a portable mode selector, or a bundle sufficient for headed execution are superseded for the v1.0.0 Windows portable only; they are retained as historical design context.

The source/development product retains Background and Visible. The self-contained Windows portable supports only Background, communicates that effective mode, and excludes headed Chrome for Testing. This is a CLI/runtime distribution capability, not a change to Engine contracts or prospecting semantics.

P106/R06 now requires the bundled browser needed for Background only. P106/R14 still requires a documented redistribution basis and required notices for the **exact** remaining headless payload, plus proof that headed Chrome for Testing is absent. R14 may PASS only after that audit. P107/R08–R10/R19 packaged validation covers Background, while source-mode validation preserves Visible. P108 documents the distinction, prepares the RC and checksum, and leaves R20 to the owner. No Playwright downgrade, system-browser dependency, release publication, or A3 action is authorized by this amendment.

## Owner amendment — 2026-10-08: Edge-based portable runtime

Status: ACCEPTED. This decision supersedes the prior v1.0.0 portable requirements to bundle Chromium, Chrome for Testing, Chrome Headless Shell, or any browser; be browser-self-contained; or omit Visible from the portable. Earlier text and the Background-only amendment remain historical, not operative for portable packaging.

Both source/development and Windows portable support Background and Visible with Microsoft Edge Stable through Playwright 1.61.0 `channel="msedge"`. Background is the desired default pending Edge-specific R04 evidence. The portable remains self-contained for Python and application/runtime dependencies; installed Edge Stable is an explicit external prerequisite. BrowserRuntime owns launches and cleanup; no Engine business contract, extraction, normalization, identity, deduplication, or export semantics change.

P105/R04 must be repeated for Edge headed/headless. P106/R06 becomes **Browser Runtime Availability** (both modes, controlled missing/blocked failure, no Playwright-managed cache or bundled browser). P106/R14 audits Python, Rich, Playwright, openpyxl, PyInstaller runtime and other actual distributed dependencies; browser redistribution is NOT APPLICABLE. P106/R05/R07/R16 must be remeasured on the no-browser artifact. P107/R08–R10/R19 requires Edge-based clean/isolated and packaged smoke; P108 finalizes contracts, docs, ZIP and SHA-256. R20 remains owner-only and A3 remains unauthorized.

## Owner exception — 2026-10-08: R08 and R19 for the initial release

The owner waives a separate clean/isolated Windows-machine run for v1.0.0 only. Preserve the original R08 criterion above, but record its actual outcome as **OWNER_WAIVED / DEFERRED_POST_RELEASE**, not PASS/FAIL/BLOCKED. No second clean Windows machine is available; Windows Sandbox is unavailable. Relocation and cache-independent execution on the primary host do not constitute R08. Microsoft Edge Stable is an external prerequisite. Residual machine-specific compatibility risk is accepted and will be investigated after release, with ordinary patch maintenance if needed.

R19 is amended to require complete source regression and packaged-product smoke on the current Windows host. It must not be reported as external-machine validation. R09, R10 and remaining P107/P108 contracts stay mandatory; the final artifact and owner-only R20 remain unchanged. A3 is not authorized.

**END — V1-0-0-MASTER-IMPLEMENTATION-DESIGN**

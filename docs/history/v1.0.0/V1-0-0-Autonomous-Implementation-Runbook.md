# Prospector CLI — v1.0.0 Autonomous Implementation Runbook

**Status:** READY FOR OWNER APPROVAL / ACTIVATION  
**Target:** Prospector CLI `v1.0.0`  
**Document type:** Autonomous Implementation Runbook  
**Primary authority:** `ADR-010 — Stable CLI UX, Windows Portable Distribution and v1.0.0 Release Freeze`  
**ADR status:** `APPROVED — AUTHORITATIVE PROJECT AUTHORITY`  
**Secondary authority:** `V1-0-0-Master-Implementation-Design.md`  
**Master status:** `ACCEPTED — AUTHORITATIVE PROJECT AUTHORITY`  
**Predecessor:** `v0.9.x — OWNER ACCEPTED / COMPLETE`  
**Accepted functional implementation baseline:** `c7193d55a36618e934e29a9678b3f9b01e9b6543`  
**Expected v1.0.0 starting repository state:** `71cb7f8981281ce68a2e9936ba01554e69e8c7ed`

---

# 1. Purpose

This Runbook defines the operational procedure Codex SHALL follow to implement Prospector CLI `v1.0.0`.

It converts the approved ADR and accepted Master into an executable engineering sequence covering:

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

It also governs:

```text
R01–R20 evidence gates
offline execution
live external validation
packaging
clean-machine testing
Git operations
release authorization
STOP / OWNER REVIEW behavior
```

This Runbook SHALL NOT expand the functional scope defined by ADR-010.

---

# 2. Authority Order

Codex SHALL resolve conflicts using:

```text
1. ADR-010
2. V1-0-0-Master-Implementation-Design.md
3. this Autonomous Implementation Runbook
4. accepted v0.9.x contracts
5. current source/tests/documentation
```

A lower-level artifact SHALL NOT override a higher-level decision.

When the authorities do not answer a material architectural or business-policy question:

```text
STOP / OWNER REVIEW
```

Do not infer a new rule.

---

# 3. Interpretation of Authorization

The Master authorizes the **scope** of implementation.

This Runbook controls **how and when** that scope may be executed.

The following states are distinct:

```text
DESIGN AUTHORIZED
!=
RUNBOOK APPROVED
!=
IMPLEMENTATION ACTIVATED
!=
LIVE EVIDENCE AUTHORIZED
!=
RELEASE AUTHORIZED
```

No stage SHALL infer authorization for a later stage.

---

# 4. Authorization Classes

The v1.0.0 work SHALL use four explicit authorization classes.

## A0 — Inspection Only

Allowed:

- read code;
- inspect Git;
- inspect documentation;
- inspect dependencies;
- inspect existing tests;
- create/update local planning documents under ignored `temp/`.

Not allowed:

- production code edits;
- dependency installation;
- branch creation;
- commits;
- push;
- live Google Maps;
- packaging publication;
- release operations.

---

## A1 — Local / Offline Implementation

Allows:

- branch creation/change if explicitly included in activation;
- source edits;
- tests;
- documentation;
- Rich implementation;
- observer/metrics implementation;
- cancellation implementation;
- logging/filesystem hardening;
- PyInstaller build configuration;
- local packaging experiments;
- offline test execution;
- local artifact generation.

Does NOT automatically allow:

- Google Maps live evidence;
- external Website Engine live evidence;
- clean-machine testing on another system;
- commit/push unless explicitly activated;
- tag;
- GitHub Release;
- release artifact publication.

---

## A2 — Live / External Evidence

Allows only the explicitly named live validation.

Examples:

- headed vs headless Google Maps comparison;
- real source execution;
- Website enrichment live evidence;
- packaged Google Maps smoke;
- live cancellation tests.

This authorization SHALL be bounded to:

- purpose;
- number/type of runs where specified;
- evidence gate.

It SHALL NOT become general permission for unrelated Internet tests.

---

## A3 — Release Operations

Allows separately:

- final commit;
- push;
- tag `v1.0.0`;
- GitHub Release;
- release artifact upload;
- SHA-256 publication;
- release notes publication.

A3 SHALL NOT exist before owner acceptance of R20.

---

# 5. Default Authorization State

Before explicit owner activation:

```text
A0 INSPECTION
AUTHORIZED

A1 LOCAL IMPLEMENTATION
NOT ACTIVE

A2 LIVE EXTERNAL EVIDENCE
NOT ACTIVE

A3 RELEASE OPERATIONS
NOT ACTIVE
```

Owner approval of this Runbook may later be followed by an explicit activation message.

Codex SHALL record that activation in:

```text
temp/Planeacion/v1.0.0/OwnerAuthorization.md
```

---

# 6. Scope Freeze

No implementation may add:

- new sources;
- new prospecting capability;
- historical dedupe;
- heuristic matching;
- campaign logic;
- persistence;
- database;
- jobs;
- queues;
- concurrency;
- distributed execution;
- FastAPI;
- SaaS;
- tenancy;
- plugins;
- checkpoint/resume;
- partial execution persistence;
- remote telemetry;
- auto-update.

The release is:

```text
HARDENING
+
UX
+
OBSERVABILITY
+
PACKAGING
+
VALIDATION
+
FREEZE
```

not new Engine functionality.

---

# 7. Public Contract Freeze

The following accepted contracts SHALL remain semantically compatible:

```text
ProspectorEngine.search()
ProspectorEngine.search_many()

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

Public signature changes require:

```text
STOP / OWNER REVIEW
```

unless directly required and explicitly permitted by the approved authority documents.

Internal observability SHALL NOT silently become a new public API.

---

# 8. Architectural Boundary

Required layering:

```text
CLI / Rich presentation
          |
          v
neutral internal observability
          |
          v
ProspectorEngine
          |
          v
global/source pipelines
```

Rich SHALL NOT be imported by:

- Google Maps source;
- Website Engine;
- normalization;
- batch dedupe;
- domain models;
- Engine domain logic.

Packaging-specific behavior SHALL NOT enter prospecting business logic.

---

# 9. Git Safety

Do NOT use routine destructive operations such as:

```text
git reset --hard
git clean -fd
git clean -fdx
git stash
git rebase
git checkout -- .
git restore .
```

Do not overwrite unknown changes.

Unexpected working-tree changes:

```text
STOP / OWNER REVIEW
```

unless demonstrably created by the current authorized task.

---

# 10. Required Initial Preflight

Before P101:

```powershell
git branch --show-current
git rev-parse HEAD
git status --short
git log -1 --oneline
git remote -v
```

Expected repository baseline:

```text
HEAD:
71cb7f8981281ce68a2e9936ba01554e69e8c7ed
```

Expected predecessor branch may be:

```text
v0.9.0
```

unless owner has already created `v1.0.0`.

If HEAD differs unexpectedly:

```text
STOP / OWNER REVIEW
```

A later known documentation-only commit MAY be accepted only if explicitly owner-approved.

---

# 11. Branch Strategy

Target implementation branch:

```text
v1.0.0
```

If owner activation includes branch creation and current branch is the accepted v0.9.x state:

```powershell
git switch -c v1.0.0
```

Before creation confirm:

```powershell
git status --short
git rev-parse HEAD
```

Do not create another branch if `v1.0.0` already exists.

Do not change branch unexpectedly.

---

# 12. Local Planning Package

Create/use:

```text
temp/Planeacion/v1.0.0/
```

At minimum maintain:

```text
ADR-010-Stable-CLI-UX-Windows-Portable-Distribution-and-Release-Freeze.md
V1-0-0-Master-Implementation-Design.md
V1-0-0-Autonomous-Implementation-Runbook.md

AuthorityBaseline.md
OwnerAuthorization.md
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
```

Later add:

```text
PackagingEvidence.md
CleanMachineEvidence.md
ReleaseCandidateReport.md
OwnerAcceptanceChecklist.md
V1-0-0-Owner-Acceptance-Closure.md
FinalReleaseReport.md
```

Planning evidence under ignored `temp/` SHALL remain local unless owner changes policy.

---

# 13. Baseline Regression Before Code Changes

Before modifying production code:

```powershell
python -m compileall src tests
python -m pytest tests/unit -q
python -m pytest tests/integration -q
python -m pytest -q
```

Historical accepted baseline:

```text
unit        194 PASS
integration  68 PASS
full        262 PASS
live E2E      1 deselected
```

Counts may differ only if repository baseline legitimately changed.

Any unexpected pre-existing regression:

```text
STOP / OWNER REVIEW
```

Do not begin P102 on a broken unexplained baseline.

---

# 14. Baseline Evidence

Record in `AuthorityBaseline.md`:

```text
branch
HEAD
upstream
worktree state
Python version
platform
Playwright version
existing Chromium state where useful
baseline test results
```

Do not treat local browser caches as packaged-runtime evidence.

---

# 15. Patch Execution Rule

For each patch P101–P108:

```text
PRECHECK
  ->
IMPLEMENT / INVESTIGATE
  ->
PATCH-LOCAL TESTS
  ->
INTEGRATION TESTS
  ->
FULL OFFLINE REGRESSION when required
  ->
EVIDENCE UPDATE
  ->
PATCH AUDIT
  ->
PASS / STOP
```

Codex MAY autonomously fix patch-local defects.

Codex SHALL NOT request routine approval for safe corrections that remain strictly within the accepted patch scope.

---

# 16. Autonomous Correction Rule

Codex MAY autonomously:

- fix implementation defects introduced by the patch;
- adjust internal naming;
- add deterministic tests;
- refactor patch-local internal code;
- improve documentation;
- correct path handling;
- correct Rich rendering implementation;
- correct packaging configuration;
- correct internal observer event flow;
- correct logs/tests.

Provided that the correction:

- remains within ADR/Master;
- does not change public contract;
- does not change business semantics;
- does not add unapproved dependency;
- does not require unauthorized live access;
- does not require unauthorized Git/release action.

---

# 17. Global STOP / OWNER REVIEW Conditions

STOP immediately when:

1. accepted v0.9.x contract must change;
2. new prospecting capability appears necessary;
3. new business policy is required;
4. normalization semantics would change;
5. verified identity/dedupe semantics would change;
6. Website enrichment semantics require material redesign;
7. public Engine signature must change;
8. internal observability must become public API;
9. user progress requires fabricated metrics;
10. cancellation requires jobs/queues/concurrent orchestration;
11. BrowserRuntime ownership requires fundamental redesign;
12. Rich must enter Engine/source;
13. proprietary or paid dependency becomes required;
14. paid code signing becomes required;
15. PyInstaller is demonstrably unsuitable and a replacement packager is required;
16. Chromium distribution/licensing presents unresolved restriction;
17. headed/headless causes unexplained semantic data divergence;
18. portable runtime requires administrator installation;
19. clean machine requires undeclared prerequisite;
20. unexpected external Git changes appear;
21. unauthorized live Internet access is required;
22. unauthorized commit/push/tag/release is required;
23. source regression cannot be corrected safely within patch scope;
24. cleanup failure cannot be trusted;
25. package modifies or depends on user/developer environment outside approved portable paths;
26. evidence contradicts an ADR assumption in a way that requires policy change.

---

# 18. P101 — Baseline Audit and Release Foundations

## Authorization class

```text
A0 initially
A1 for actual changes
```

## Objective

Establish exact starting conditions.

## Tasks

Audit:

- project tree;
- entrypoints;
- public contracts;
- dependencies;
- logging;
- filesystem paths;
- version representation;
- browser assets;
- metrics;
- packaging-sensitive imports;
- tests.

---

# 19. P101 Dependency Audit — R13

Classify all dependencies as:

```text
DIRECT_RUNTIME
TRANSITIVE_RUNTIME
DEVELOPMENT_TEST
BUILD_ONLY
UNUSED_CANDIDATE
UNKNOWN
```

Do not remove anything solely based on static appearance.

For every `UNUSED_CANDIDATE`, record:

- evidence;
- imports/search;
- risk;
- whether removal is deferred.

Dependency cleanup is optional unless needed for release correctness.

---

# 20. P101 Rich Dependency

Rich is approved.

Determine a compatible pinned release.

Do not choose beta/pre-release versions without explicit need.

Record:

```text
version
license
runtime role
packaging impact
```

Install/add only under A1 activation.

---

# 21. P101 PyInstaller Dependency

PyInstaller is:

```text
BUILD_ONLY
```

Prefer keeping it separate from runtime dependencies where the repository structure permits.

Record:

- selected stable version;
- Python compatibility;
- Windows support;
- license;
- build command.

---

# 22. P101 Version Source — R17 Initial

Establish one authoritative product version:

```text
1.0.0
```

Prefer an internal module or other controlled source that can feed:

- CLI;
- packaging metadata;
- release process.

Avoid multiple independent manually edited literals.

If achieving this requires redesigning public contracts:

```text
STOP
```

---

# 23. P101 Contract Inventory — R18 Initial

Inventory:

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
errors
ExportService
CLI stable flows
export schema
limits
dedupe semantics
```

Mark each:

```text
PUBLIC_STABLE
INTERNAL
IMPLEMENTATION_DETAIL
RELEASE_UI_CONTRACT
```

This inventory is preliminary until P108.

---

# 24. P101 Metrics Inventory

Locate current instrumentation including `metrics_sink`.

Record each metric:

```text
name
owner
stage
type
current source
consumer
precision
```

Do not change semantics in P101 unless necessary for foundations.

---

# 25. P101 Filesystem Audit

Identify every location assumption for:

- exports;
- logs;
- resources;
- browser binaries;
- current working directory;
- module-relative paths.

Hardcoded developer paths are blockers.

---

# 26. P101 Tests

After any foundation changes:

```powershell
python -m compileall src tests
python -m pytest tests/unit -q
python -m pytest tests/integration -q
python -m pytest -q
```

---

# 27. P101 Exit

Pass when:

```text
R13 PASS
R17 INITIAL PASS
R18 INITIAL PASS

BASELINE KNOWN
DEPENDENCIES CLASSIFIED
CONTRACTS INVENTORIED
METRICS INVENTORIED
FILESYSTEM ASSUMPTIONS KNOWN
OFFLINE REGRESSION PASS
```

Record in:

```text
ImplementationProgress.md
ValidationMatrix.md
EvidenceIndex.md
```

---

# 28. P102 — Execution Observability and Metrics

## Authorization

```text
A1
```

## Gates

```text
R02
R03
```

---

# 29. P102 Architectural Requirement

Create a neutral internal observer/event mechanism.

Required separation:

```text
neutral internal event
        |
        +-- CLI renderer
        |
        +-- future adapter
```

Do not expose Rich types.

Do not expose terminal concepts.

Do not add telemetry persistence.

---

# 30. P102 Public API Rule

Do NOT change public signatures merely to pass an observer.

If the observer cannot be introduced internally without changing frozen public signatures:

```text
STOP / OWNER REVIEW
```

Additive-looking public parameters still count as public API changes for this gate.

---

# 31. P102 Minimum Event Semantics

Support conceptually:

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

Exact class/enum/function names are implementation details.

---

# 32. P102 No-Op Observer

No observer must remain a valid execution mode.

Results MUST be semantically identical:

```text
with observer
==
without observer
```

except for instrumentation side effects.

---

# 33. P102 metrics_sink Reconciliation

Existing `metrics_sink` SHALL NOT coexist as a second competing telemetry architecture.

Allowed strategies:

- adapt;
- wrap;
- migrate;
- preserve as low-level internal collection behind new observer.

Record rationale in `MetricsInventory.md`.

---

# 34. P102 Metric Definitions — R03

Classify every UX metric:

```text
EXACT
DERIVED
UNAVAILABLE
```

Required candidates:

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

---

# 35. P102 Candidate Semantics

Preserve:

```text
Maps candidates observed
!=
Businesses extracted
```

Do not introduce ambiguous:

```text
results_found
```

as a user-facing replacement.

---

# 36. P102 Progress Semantics

A progress event MAY represent:

```text
stage active
count observed
current / total
stage completed
elapsed time
```

Do not emit fake percentage.

---

# 37. P102 Normalization Instrumentation

Normalization may emit start/end/timing/count events.

It SHALL:

- run exactly once/query;
- preserve output;
- preserve ordering;
- preserve original/normalized correspondence.

---

# 38. P102 Deduplication Instrumentation

Batch selector may expose:

```text
verified
unverified
suppressed
exportable
```

but CLI SHALL NOT decide duplicates.

Deduplication remains in the existing batch layer.

---

# 39. P102 Tests

At minimum:

- no-op observer;
- observer enabled;
- event order only where semantically necessary;
- metric ownership;
- single search;
- batch;
- recoverable issue;
- controlled failure;
- normalization once;
- dedupe unchanged;
- no Rich import below presentation;
- identical results observer/no observer.

---

# 40. P102 Validation

Run:

```powershell
python -m compileall src tests
python -m pytest tests/unit -q
python -m pytest tests/integration -q
python -m pytest -q
```

---

# 41. P102 Exit

```text
R02 PASS
R03 PASS
PUBLIC CONTRACTS UNCHANGED
RICH ABSENT FROM ENGINE/SOURCE
FULL OFFLINE PASS
```

---

# 42. P103 — Final Rich CLI UX

## Authorization

```text
A1
```

## Gate

```text
R01
```

---

# 43. P103 Main Application

Implement professional Rich-based presentation.

Required semantic menu:

```text
Prospector CLI
v1.0.0

1. New Search
2. Multiple Searches
3. Exit
```

Exact border/color/font style is non-normative.

---

# 44. P103 Session Loop

The CLI SHALL support repeated operations without relaunch.

Test:

```text
search
-> return
-> search
-> export
-> return
-> batch
-> return
-> exit
```

---

# 45. P103 Single Search Flow

Required:

```text
capture
review
edit/back
confirm
browser choice
effective config
execute
progress
summary
view/export/back
```

No source execution before confirmation.

---

# 46. P103 Batch Flow

Interactive batch remains:

```text
2–3 queries
```

Engine remains:

```text
1–5
```

Do not change either boundary.

---

# 47. P103 Browser Choice

After final input confirmation, before BrowserRuntime:

```text
Background
Visible
```

Desired default remains background pending R04.

Do not create the browser before this selection.

---

# 48. P103 Website Enrichment

Always enabled for the CLI.

Do not add user toggle.

Display:

```text
Website enrichment: Enabled
```

as current effective configuration where appropriate.

---

# 49. P103 Rich Progress — R01

Implement two conceptual views:

```text
GLOBAL PIPELINE

SOURCE PIPELINE
```

Allow:

- spinner/indeterminate stage;
- determinate current/total;
- elapsed time;
- macro messages;
- clean refresh.

---

# 50. P103 Progress Accuracy

Only show determinate progress where total is meaningful.

Examples:

```text
31 / 50
```

allowed.

```text
73%
```

without a real denominator is prohibited.

---

# 51. P103 Summary

Every search shows a summary before individual results.

Batch:

- per-query summary;
- consolidated summary.

Only applicable metrics shall appear.

---

# 52. P103 Result Viewer

Results displayed in pages of:

```text
10
```

Provide navigation appropriate to current position.

Do not print all records automatically.

---

# 53. P103 Export UX

Output file remains primary full result.

Clearly display:

```text
format
path
success/failure
```

After export:

```text
Run another search
Return to main menu
```

---

# 54. P103 Error UX

Do not show stack traces in normal mode.

Present:

- human-readable status;
- recoverable issue summary;
- location of diagnostic log when relevant.

---

# 55. P103 Tests

Test semantics rather than color.

Required cases:

- main menu;
- invalid selection;
- single search flow;
- edit before confirmation;
- back;
- rejection of confirmation;
- effective config;
- batch 2;
- batch 3;
- pagination;
- export route;
- repeated searches;
- partial;
- failed query;
- batch interrupted presentation.

---

# 56. P103 Validation

```powershell
python -m compileall src tests
python -m pytest tests/unit -q
python -m pytest tests/integration -q
python -m pytest -q
```

---

# 57. P103 Exit

```text
R01 PASS
RICH PRESENTATION ONLY
REPEATED SESSION PASS
SUMMARY PASS
PAGINATION PASS
OFFLINE REGRESSION PASS
```

---

# 58. P104 — Cancellation, Logging and Filesystem Hardening

## Authorization

```text
A1
```

Live cancellation validation remains A2.

## Gates

```text
R09
R10
R11
R12
```

---

# 59. P104 Ctrl+C Contract

During active execution:

```text
Ctrl+C
```

shall initiate controlled cancellation request.

Required prompt:

```text
Cancel current execution?
All unexported results from this execution will be lost.
[y/N]
```

Exact wording may vary without changing semantics.

---

# 60. P104 Continue on No

If cancellation is rejected:

```text
execution continues
```

If the synchronous runtime makes safe continuation impossible with a straightforward implementation:

```text
STOP / OWNER REVIEW
```

Do not silently redefine No as cancellation.

---

# 61. P104 Confirmed Cancellation

On Yes:

- request cancellation;
- unwind safely;
- BrowserRuntime cleanup;
- discard unexported state;
- no checkpoint;
- no resume;
- no recovery file;
- no auto-export.

Return to menu when cleanup state is trustworthy.

---

# 62. P104 Cancellation Implementation Constraint

Do NOT introduce:

- job queue;
- worker orchestration;
- batch concurrency;
- generic async framework;
- processing service.

Use the smallest cooperative mechanism compatible with the synchronous architecture.

---

# 63. P104 Cancellation Failure

If cleanup fails or state becomes untrustworthy:

- do not continue normal session;
- show safe user message;
- log diagnostic;
- terminate application if needed.

Cleanup failure is more important than maintaining the menu loop.

---

# 64. P104 Windows Console Close — R10

Implement best-effort handling where appropriate.

Do not promise interactive confirmation for:

- console X;
- logout;
- shutdown;
- forced termination.

Record actual behavior.

---

# 65. P104 Logs — R11

Create portable-local:

```text
logs/
```

Use rotating logging.

Choose bounded:

```text
maxBytes
backupCount
```

appropriate to CLI diagnostics.

Document selected values.

---

# 66. P104 Logging Safety

Do not deliberately log:

- full prospect exports;
- complete HTML;
- browser storage;
- credentials;
- secrets;
- arbitrary page content.

URLs should only be logged where diagnostically necessary and safe under existing source policy.

---

# 67. P104 Application Root

Create a centralized portable-aware path mechanism for:

```text
app root
exports/
logs/
packaged resources
```

Do not derive output from arbitrary current working directory if packaged application root is known.

---

# 68. P104 Exports — R12

Default:

```text
<portable-root>/exports/
```

Validate:

- CSV;
- XLSX;
- batch;
- repeated export;
- unique names;
- zero rows;
- write error;
- spaces in path;
- cleanup after error.

---

# 69. P104 Offline Tests

Create controlled cancellation tests without requiring Google Maps.

Use fakes/stubs at safe seams.

Do not make default tests depend on timing-sensitive public Internet calls.

---

# 70. P104 Live Tests

R09 live cancellation across real pipeline stages requires:

```text
A2 LIVE AUTHORIZATION
```

Do not automatically run.

---

# 71. P104 Validation

Offline:

```powershell
python -m compileall src tests
python -m pytest tests/unit -q
python -m pytest tests/integration -q
python -m pytest -q
```

Then, only when A2 activated, execute bounded live cancellation evidence.

---

# 72. P104 Exit

Offline exit may record:

```text
R11 PASS
R12 PASS
R09 OFFLINE PASS / LIVE PENDING
R10 CONTROLLED PASS / PACKAGED EVIDENCE PENDING
```

Final R09/R10 may remain pending until live/packaged phases.

Do not falsely mark complete.

---

# 73. P105 — Browser Mode Validation and Runtime Stabilization

## Authorization

```text
A2 REQUIRED
```

No P105 live evidence without explicit owner authorization.

## Gate

```text
R04
```

---

# 74. P105 Preconditions

Require:

- P101–P104 offline PASS;
- clean offline regression;
- no active architecture blocker;
- observer metrics capable of measuring comparison.

---

# 75. P105 Comparison Design

Use controlled-equivalent queries.

Record:

```text
query
limit
mode
candidate count
extracted count
verified
unverified
issues
stage timings
total time
cleanup
```

Compare:

```text
VISIBLE / HEADED
BACKGROUND / HEADLESS
```

---

# 76. P105 Run Count

Use enough runs to determine operational equivalence without unnecessary public traffic.

Prefer:

- small/medium representative limits;
- same query pair where practical;
- repeat only when evidence is inconclusive.

Do not turn this into performance benchmarking at scale.

---

# 77. P105 Decision

Preferred:

```text
Background default
Visible optional
```

Fallback already owner-approved:

```text
Visible default
Background optional
```

If systematic unexplained data divergence appears:

```text
STOP / OWNER REVIEW
```

Do not pick a default by preference alone.

---

# 78. P105 Evidence

Record in a dedicated section/file such as:

```text
BrowserModeEvidence.md
```

and update:

```text
ValidationMatrix.md
EvidenceIndex.md
ImplementationProgress.md
```

---

# 79. P105 Exit

```text
R04 PASS
DEFAULT MODE RESOLVED
FULL OFFLINE REGRESSION PASS
```

---

# 80. P106 — Windows Portable Packaging

## Authorization

```text
A1 local packaging
```

No external publication.

## Gates

```text
R05
R06
R07
R14
R15
R16
```

---

# 81. P106 Build Tool

Primary:

```text
PyInstaller
```

Topology:

```text
onedir
```

Do not substitute another packager without STOP if PyInstaller proves unsuitable.

---

# 82. P106 Build Dependency

Treat PyInstaller as build tooling.

Do not require end users to install it.

---

# 83. P106 Target

Build:

```text
Windows 10/11 x64
```

The build itself should occur on a compatible Windows environment.

---

# 84. P106 Portable Layout

Expected conceptual artifact:

```text
Prospector-CLI-v1.0.0-win64/
├── prospector.exe
├── packaged runtime/
├── Chromium assets/
├── exports/
├── logs/
├── LICENSE
├── THIRD_PARTY_NOTICES*
└── user documentation
```

Actual `_internal/` or browser directory names may follow PyInstaller/Playwright conventions.

---

# 85. P106 Chromium — R06

Bundle browser assets compatible with the exact Playwright version.

The user must not run:

```text
playwright install
```

The executable must not depend on an existing developer Playwright cache.

---

# 86. P106 Browser Mode Bundle

Bundle enough Chromium/runtime support for:

- selected default;
- alternate supported mode.

Do not build background-only if Visible is a required option.

---

# 87. P106 Resource Resolution

Package must resolve:

- app version;
- browser assets;
- exports;
- logs;
- notices/docs;

independently of repo paths.

---

# 88. P106 PyInstaller onedir — R05

Validate:

- import discovery;
- Rich;
- Playwright;
- openpyxl;
- stdlib resources;
- project modules;
- executable launch.

No source Python installation may be required to run artifact.

---

# 89. P106 onefile

`onefile` MAY be explored only after `onedir` works.

Do not spend meaningful release time optimizing onefile unless there is clear operational value.

`onedir` passing fully satisfies ADR.

---

# 90. P106 Relocation — R07

Test:

- Desktop-like location;
- nested location;
- path with spaces;
- renamed parent folder;
- copied directory.

USB test:

```text
DESIRABLE
NON-BLOCKING
```

---

# 91. P106 Artifact Size — R16

Record:

```text
onedir uncompressed size
ZIP size
prospector.exe size
Chromium/browser asset size where useful
cold app startup
browser startup
```

No arbitrary target.

Mark:

```text
ACCEPTABLE
or
OWNER REVIEW
```

only if operationally extreme.

---

# 92. P106 Third-Party Notices — R14

Audit licenses for shipped components including at minimum:

- Rich;
- PyInstaller where relevant;
- Playwright;
- Chromium;
- openpyxl;
- direct runtime dependencies actually shipped.

Do not fabricate license obligations.

Use official package/project license sources where needed.

Unresolved mandatory license obligations block release.

---

# 93. P106 SignPath — R15

Optional.

Investigate only enough to establish:

```text
FREE?
ELIGIBLE?
LOW FRICTION?
```

If all yes:

```text
MAY CONTINUE
```

Otherwise:

```text
SKIPPED / UNSIGNED RELEASE ACCEPTED
```

No payment.

No release delay.

---

# 94. P106 SHA-256

Development artifacts may have hashes for evidence.

Final mandatory release SHA-256 belongs to P108.

---

# 95. P106 Validation

After build:

- launch locally outside repo;
- navigate menu;
- verify version;
- verify directories;
- use controlled/non-live paths where possible.

Google Maps packaged live execution belongs to A2/P107.

---

# 96. P106 Exit

```text
R05 PASS
R06 PASS
R07 PASS
R14 PASS
R15 PASS/SKIPPED NON-BLOCKING
R16 PASS

PORTABLE BUILD EXISTS
NO PYTHON REQUIRED
NO MANUAL PLAYWRIGHT SETUP
```

---

# 97. P107 — Clean-Machine and Packaged Regression

## Authorization

Requires:

```text
A2 for live packaged Google Maps
```

and practical access to a clean/isolated Windows environment.

## Gates

```text
R08
R19
```

---

# 98. P107 Clean Environment Definition

Environment shall not rely on:

- repository;
- developer virtualenv;
- project Python installation;
- Playwright developer browser cache;
- source tree.

Normal Windows system components are acceptable.

---

# 99. P107 Installation Experience

Normative user flow:

```text
download ZIP
extract
open folder
run prospector.exe
```

No installer required.

No admin rights required.

---

# 100. P107 Required Smoke

Validate:

```text
launch
main menu
single search
batch
default browser mode
alternate browser mode
progress
summary
pagination
CSV
XLSX
repeated search
logs
normal exit
Ctrl+C
```

---

# 101. P107 Search Inputs

Use controlled representative inputs.

Do not use extreme limits merely to stress system.

Evidence should prove usability, not catalog completeness.

---

# 102. P107 Clean-Machine Filesystem

Verify:

```text
exports/
logs/
runtime/browser lookup
path with spaces
moved portable
non-admin execution
```

---

# 103. P107 Ctrl+C Live — R09 Final

Exercise cancellation at representative stages where practical.

Examples:

- feed;
- detail;
- website.

Do not force every possible timing window if unsafe/unreliable.

Required semantic proof:

- confirmation appears when supported;
- Yes cancels;
- cleanup occurs;
- no corrupt export;
- no checkpoint;
- no resume.

---

# 104. P107 Console Close — R10 Final

Test packaged console X where practical.

Record actual result.

Requirement:

```text
best-effort cleanup
```

not guaranteed user confirmation.

---

# 105. P107 Full Regression — R19

Run source regression on implementation state:

```powershell
python -m compileall src tests
python -m pytest tests/unit -q
python -m pytest tests/integration -q
python -m pytest -q
```

Then packaged smoke.

Do not claim packaged executable ran the pytest suite unless it actually did.

R19 consists of:

```text
SOURCE REGRESSION
+
PACKAGED PRODUCT SMOKE
```

---

# 106. P107 Evidence

Create/update:

```text
CleanMachineEvidence.md
PackagingEvidence.md
ValidationMatrix.md
EvidenceIndex.md
AuditDiff.md
```

Include:

- Windows version;
- machine/environment type;
- absence of Python dependency;
- artifact hash;
- test scenarios;
- pass/fail;
- known limitations.

---

# 107. P107 Exit

```text
R08 PASS
R09 PASS
R10 PASS
R19 PASS

CLEAN MACHINE PASS
PACKAGED LIVE PASS
NO ENVIRONMENT DEPENDENCY
```

---

# 108. P108 — Contract Freeze, Release Candidate and Closure

## Authorization

Local P108 work:

```text
A1
```

Owner RC acceptance required before A3.

## Gates

```text
R17
R18
R20
```

---

# 109. P108 Contract Audit — R18

Re-read implementation against:

- ADR-010;
- Master;
- this Runbook.

Audit public contracts:

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
errors
ExportService
```

Confirm:

```text
UNCHANGED
or
AUTHORIZED COMPATIBLE HARDENING
```

Any unknown breaking change:

```text
STOP
```

---

# 110. P108 CLI Contract Freeze

Freeze semantic behavior:

- main menu;
- single flow;
- batch flow;
- confirmation;
- edit/back;
- browser selection;
- progress semantics;
- summary;
- pagination = 10;
- cancellation;
- exports;
- paths;
- statuses.

Do not freeze colors/borders unless intentionally documented.

---

# 111. P108 Version Source — R17 Final

Verify one source produces:

```text
1.0.0
```

across:

- CLI display;
- packaging;
- release metadata/process.

No silent mismatch allowed.

---

# 112. P108 User Documentation

Complete documentation for:

- purpose;
- Windows support;
- download;
- extraction;
- run;
- menu;
- single;
- batch;
- limits;
- browser modes;
- progress;
- metrics;
- result viewer;
- export;
- exports path;
- logs;
- cancellation;
- dedupe limitation;
- troubleshooting;
- license.

---

# 113. P108 Developer Documentation

Update:

- architecture;
- contributor setup;
- tests;
- packaging;
- release workflow;
- dependencies;
- frozen contracts;
- post-v1 boundary.

---

# 114. P108 Release Candidate

Build final RC:

```text
Prospector-CLI-v1.0.0-win64.zip
```

No `RC` suffix is required if artifact is rebuilt identically for final release, but evidence must make candidate identity clear.

Record SHA-256.

---

# 115. P108 Final Regression

Before owner handoff:

```powershell
python -m compileall src tests
python -m pytest tests/unit -q
python -m pytest tests/integration -q
python -m pytest -q
git diff --check
```

Also verify packaged RC smoke evidence remains valid for the same artifact/build.

---

# 116. P108 Release Candidate Report

Create:

```text
ReleaseCandidateReport.md
```

Include:

```text
branch
HEAD
version
artifact name
artifact SHA-256
artifact size
Windows target
browser default
alternative browser mode
test totals
R01–R19 statuses
known accepted limitations
active blockers
release blockers
owner actions required
```

---

# 117. R20 — Owner Release Candidate Acceptance

R20 SHALL NOT be self-approved by Codex.

Codex must present the RC to the owner.

Owner validates/accepts:

- UX;
- usability;
- progress;
- metrics;
- summaries;
- pagination;
- cancellation;
- exports;
- browser mode;
- portability;
- package structure;
- docs;
- limitations.

Until explicit owner acceptance:

```text
R20 PENDING OWNER ACCEPTANCE
```

---

# 118. Release Barrier

Before R20:

Do NOT:

```text
tag v1.0.0
create GitHub Release
publish stable artifact
declare v1.0.0 RELEASED
```

The highest allowed status is:

```text
IMPLEMENTED
VALIDATED
RELEASE CANDIDATE READY
OWNER ACCEPTANCE PENDING
```

---

# 119. A3 Release Authorization

After owner accepts R20, release still requires explicit A3 authorization.

A valid activation should clearly authorize some/all of:

```text
final commit
push
tag v1.0.0
GitHub Release
artifact upload
SHA-256 publication
release notes
```

Do not infer these from R20 acceptance alone unless the owner explicitly combines acceptance and release authorization.

---

# 120. Release Operations

Only under A3:

1. confirm clean intended Git state;
2. create final release commit if needed;
3. push approved branch;
4. create annotated/lightweight tag per established repository policy;
5. push `v1.0.0` tag;
6. create GitHub Release;
7. upload:
   - portable ZIP;
   - checksum;
   - relevant release files;
8. publish release notes;
9. verify remote release state.

If repository has no established tag policy, use the simplest standard Git tag unless owner specifies otherwise.

Do not invent extra release channels.

---

# 121. Final Artifact SHA-256

The checksum SHALL correspond exactly to the uploaded stable artifact.

If artifact is rebuilt after checksum generation:

```text
old hash invalid
```

Generate a new one.

---

# 122. Final Release State

Only after successful A3 verification may documentation state:

```text
Prospector CLI v1.0.0
OWNER ACCEPTED
STABLE
TAGGED
RELEASED
CONTRACTS FROZEN
WINDOWS PORTABLE ARTIFACT PUBLISHED
```

---

# 123. Post-Release Freeze

After release:

```text
Prospector CLI -> MAINTENANCE MODE
```

No immediate feature expansion.

Next architecture initiative:

```text
Prospector Engine extraction
```

followed by external consumers such as:

```text
CLI
API
future multitenant platform
```

under future authorities.

---

# 124. Validation Matrix

Initialize:

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

Allowed statuses:

```text
PENDING
IN_PROGRESS
PASS
FAIL
BLOCKED
OPTIONAL_SKIPPED
OWNER_ACCEPTANCE_PENDING
```

Do not mark PASS without evidence.

---

# 125. Gate-to-Patch Mapping

```text
P101
R13
R17 initial
R18 initial

P102
R02
R03

P103
R01

P104
R09
R10
R11
R12

P105
R04

P106
R05
R06
R07
R14
R15
R16

P107
R08
R09 final live
R10 final packaged
R19

P108
R17 final
R18 final
R20
```

---

# 126. Patch Completion Matrix

A patch is not complete merely because code was written.

Each patch SHALL finish with:

```text
CODE/CONFIG COMPLETE
TESTS PASS
EVIDENCE UPDATED
DIFF AUDITED
NO UNRESOLVED BLOCKER
GATES UPDATED
```

---

# 127. Evidence Index Rules

For each evidence item record:

```text
ID
date
patch
gate
source
command/run
result
artifact/file
interpretation
```

Do not record conclusions unsupported by evidence.

---

# 128. Implementation Progress Rules

`ImplementationProgress.md` SHALL show:

```text
current patch
completed patches
active gate
latest regression
active blocker
next allowed action
authorization class
```

---

# 129. Implementation Blockers

Every STOP condition that actually occurs gets a stable blocker ID.

Example:

```text
STOP-10-PACKAGING-01
STOP-10-HEADLESS-01
STOP-10-CONTRACT-01
```

Each blocker SHALL contain:

- trigger;
- evidence;
- affected patch/gate;
- why autonomous correction is unsafe;
- owner decision required;
- resolution if later cleared.

---

# 130. No Silent Gate Reinterpretation

Codex SHALL NOT weaken a gate to achieve PASS.

Examples prohibited:

- calling a developer machine “clean”;
- calling source run “packaged”;
- calling synthetic IDs “live P92 evidence”;
- calling CLI output “telemetry”;
- calling a ZIP portable if it depends on local Python;
- calling headless equivalent based only on startup success.

---

# 131. Offline vs Live Separation

Offline suite SHALL remain Internet-independent by default.

Live checks SHALL:

- be explicit;
- be isolated;
- not run from default `pytest`;
- not become required for ordinary contributor regression.

---

# 132. Packaging vs Source Separation

Passing source tests does not prove packaging.

Passing packaging startup does not prove source correctness.

Both are required.

---

# 133. Release vs Implementation Separation

Passing P101–P108 implementation code does not automatically equal release.

The sequence remains:

```text
IMPLEMENT
VALIDATE
BUILD RC
OWNER ACCEPT
RELEASE AUTHORIZE
TAG/PUBLISH
```

---

# 134. Documentation Reconciliation

At the end of every material patch, review affected official docs.

Do not leave official docs describing stale current behavior.

Historical planning evidence may preserve old states when clearly contextualized.

---

# 135. Official Documentation Authority

By final P108, official `README.md` and `docs/` SHALL reflect released behavior.

Local `temp/Planeacion/v1.0.0/` remains detailed implementation evidence.

Do not rely on temp alone for final architecture truth.

---

# 136. README Final Role

README SHALL provide external-user entry information:

- what it is;
- downloadable Windows release;
- source/developer path separately;
- usage overview;
- supported modes;
- known limitations.

Do not turn README into the entire engineering dossier.

---

# 137. Dependency Change Rule

Approved new dependencies currently include:

```text
Rich
PyInstaller as build tooling
```

Additional dependency:

```text
STOP / OWNER REVIEW
```

unless purely transitive to an already approved dependency and not directly selected by project code.

---

# 138. Internet Research Rule

Codex MAY consult official technical documentation when implementation requires clarification for:

- Rich;
- PyInstaller;
- Playwright;
- Chromium packaging;
- Python logging;
- Windows console control;
- dependency licensing.

Prefer:

```text
official docs
official repository
official license files
```

Do not use random blogs as normative evidence when primary sources exist.

---

# 139. Packaging Research Rule

If PyInstaller official guidance and actual spike diverge:

actual controlled evidence wins for project behavior.

If resolving the issue would require switching packager:

```text
STOP
```

---

# 140. Headless Research Rule

The ADR-approved desired default does not override evidence.

Evidence selects between:

```text
Background default
or
Visible default
```

No third semantic mode is introduced without authority.

---

# 141. Performance Rule

Do not optimize prematurely.

Measure first.

Performance fixes must:

- address obvious release regression;
- preserve behavior;
- remain sequential.

No concurrency for performance.

---

# 142. Metrics Future-Proofing Rule

Internal observability may be structurally reusable later.

Do NOT implement:

- collector backend;
- telemetry database;
- metrics server;
- exporter;
- analytics dashboard.

That belongs post-v1.

---

# 143. Error Handling Rule

Normal user output:

```text
clean
actionable
non-technical
```

Logs:

```text
diagnostic
structured enough to troubleshoot
```

Do not hide fatal application state just to keep UX clean.

---

# 144. Cancellation UX Rule

Cancellation confirmation must not be represented as successful until cleanup outcome is known.

Possible final messages:

```text
Execution cancelled safely.
```

or:

```text
Execution cancelled, but runtime cleanup could not be fully verified.
The application will close.
```

Exact wording is implementation detail.

---

# 145. Export Integrity Rule

Do not export in-progress internal objects merely to preserve work during cancellation.

Cancellation is explicitly lossy for unexported results.

---

# 146. Portable Root Rule

User-facing writable directories:

```text
exports/
logs/
```

SHALL belong to the portable distribution structure.

Do not scatter files through:

- repo;
- temp developer directories;
- current shell path;

without intentional reason.

---

# 147. Build Reproducibility

The release process SHALL document enough information to rebuild:

- Python version;
- dependency versions;
- PyInstaller version;
- Playwright version;
- browser revision;
- build command/config.

Perfect byte-for-byte reproducibility is not a mandatory v1.0.0 gate unless naturally achieved.

---

# 148. RC Identity

Release candidate evidence SHALL bind to:

```text
source HEAD
build config
artifact filename
artifact SHA-256
```

Do not accept one artifact and publish a different unvalidated artifact without re-validation.

---

# 149. Owner Acceptance Checklist

Before R20, create:

```text
OwnerAcceptanceChecklist.md
```

Include:

```text
[ ] Main menu
[ ] Single search
[ ] Batch
[ ] Input correction
[ ] Confirmation
[ ] Browser mode
[ ] Progress
[ ] Metrics
[ ] Summary
[ ] Pagination
[ ] CSV
[ ] XLSX
[ ] Repeated execution
[ ] Ctrl+C
[ ] Logs
[ ] Portable relocation
[ ] Clean machine
[ ] Documentation
[ ] Known limitations
[ ] Artifact SHA-256
```

Owner acceptance SHALL be explicitly recorded.

---

# 150. Final Closure Documentation

After release create/update:

```text
V1-0-0-Owner-Acceptance-Closure.md
FinalReleaseReport.md
```

Final report SHALL record:

```text
implementation baseline
release commit
tag
GitHub Release
artifact
SHA-256
tests
gates R01–R20
known accepted limitations
post-release state
```

---

# 151. Expected Known Limitations

Do not “fix” accepted limitations during release unless separately authorized.

At minimum preserve/document:

- verified-only interquery dedupe;
- `UNVERIFIED` observations may appear commercially duplicated;
- Google Maps is external and can produce recoverable partial results;
- first packaged release targets Windows x64;
- unsigned executable may trigger Windows reputation/security warnings;
- no auto-update;
- no persistence/checkpoints;
- no API/SaaS.

---

# 152. Commit Policy During Implementation

If implementation activation does NOT explicitly authorize commits:

- modify locally;
- test;
- keep evidence;
- do not commit.

If commits are authorized:

prefer logically meaningful patch commits or coherent implementation commits.

Do not force exactly one commit per P101–P108.

Do not push unless separately authorized.

---

# 153. Push Policy

Push requires explicit owner authorization.

Local commits do not imply push authorization.

---

# 154. Tag Policy

Tag `v1.0.0` requires:

```text
R20 PASS
+
A3 RELEASE AUTHORIZATION
```

Never create the tag early “for testing”.

Use untagged RC artifacts before release.

---

# 155. GitHub Release Policy

GitHub Release is the public stable release boundary.

Do not create a draft/published release unless A3 authorizes it.

If owner authorizes a draft release separately, record that distinction.

---

# 156. Artifact Upload Policy

Only upload the accepted artifact matching the final recorded SHA-256.

Do not upload developer-local intermediate packages as stable release files.

---

# 157. Failure Handling

When an authorized step fails:

1. preserve evidence;
2. diagnose;
3. determine whether patch-local;
4. fix autonomously if safe;
5. rerun relevant tests;
6. update evidence;
7. continue if PASS.

If failure crosses STOP boundary:

```text
STOP / OWNER REVIEW
```

---

# 158. No Premature Success

Never report:

```text
v1.0.0 COMPLETE
```

before release closure.

Use accurate intermediate statuses:

```text
P102 COMPLETE
OFFLINE VERIFIED
PACKAGING VERIFIED
RC READY
OWNER ACCEPTANCE PENDING
RELEASE AUTHORIZATION PENDING
```

---

# 159. Final Pre-Release Audit

Before R20 handoff:

```powershell
git status --short
git diff --stat
git diff --check
git log -1 --oneline
```

Also audit:

- version;
- docs;
- dependencies;
- tests;
- artifact;
- checksum;
- gates.

---

# 160. Final Release Audit

After A3 publication, verify:

```text
branch remote aligned as intended
release commit exists
tag v1.0.0 points to intended commit
GitHub Release exists
artifact downloadable
checksum matches published artifact
release notes correct
```

---

# 161. Final State Machine

```text
ADR-010 APPROVED
        |
        v
MASTER ACCEPTED
        |
        v
RUNBOOK APPROVED
        |
        v
OWNER ACTIVATES IMPLEMENTATION
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
OWNER AUTHORIZES LIVE EVIDENCE
        |
        v
P105
        |
        v
P106
        |
        v
OWNER AUTHORIZES PACKAGED LIVE/CLEAN EVIDENCE
        |
        v
P107
        |
        v
P108 LOCAL RELEASE PREP
        |
        v
RC READY
        |
        v
OWNER R20 ACCEPTANCE
        |
        v
OWNER A3 RELEASE AUTHORIZATION
        |
        v
TAG + GITHUB RELEASE + ARTIFACT
        |
        v
v1.0.0 OWNER ACCEPTED / STABLE / RELEASED
        |
        v
CLI MAINTENANCE FREEZE
```

---

# 162. Suggested Owner Activation Language

After this Runbook is approved, an implementation activation may state:

```text
LOCAL IMPLEMENTATION AUTHORIZED.

Authorize creation/use of branch v1.0.0 from the accepted v0.9.x closure baseline.

Authorize local implementation of P101–P104 and local/offline portions of P106–P108 according to ADR-010, the accepted Master and the approved Runbook.

Authorize installation of the already-approved Rich runtime dependency and PyInstaller build tooling using compatible pinned stable versions.

Do not authorize live Google Maps evidence, packaged live validation, commits, push, tag, GitHub Release or artifact publication unless separately stated.

Codex may autonomously correct patch-local defects and continue while all STOP conditions remain clear.
```

A later live authorization may state:

```text
LIVE EVIDENCE AUTHORIZED.

Authorize only the ADR/Master/Runbook live validation required for P105 and the explicitly named live portions of P104/P107.

No general browsing, release operations, tag or publication are authorized by this statement.
```

A later release authorization may state:

```text
RELEASE AUTHORIZED.

R20 is OWNER ACCEPTED.

Authorize the final approved Git operations required to publish Prospector CLI v1.0.0, including the specified commit/push/tag/GitHub Release/artifact/SHA-256 operations recorded in the release plan.

No post-v1 development is authorized by this release action.
```

---

# 163. Runbook Approval Effect

When owner marks this Runbook:

```text
APPROVED — READY FOR IMPLEMENTATION
```

the engineering procedure is frozen.

Approval does NOT by itself imply:

```text
live evidence authorization
release authorization
```

unless owner explicitly combines those permissions.

---

# 164. Final Runbook Status

Current state before owner approval:

```text
ADR-010
APPROVED — AUTHORITATIVE PROJECT AUTHORITY

V1-0-0 MASTER IMPLEMENTATION DESIGN
ACCEPTED — AUTHORITATIVE PROJECT AUTHORITY

V1-0-0 AUTONOMOUS IMPLEMENTATION RUNBOOK
READY FOR OWNER APPROVAL / ACTIVATION

IMPLEMENTATION EXECUTION
NOT STARTED UNDER THIS RUNBOOK

LIVE EVIDENCE
NOT AUTHORIZED BY DEFAULT

RELEASE OPERATIONS
NOT AUTHORIZED

NEXT
OWNER APPROVES RUNBOOK
-> OWNER ACTIVATES A1
-> P101
```

## Owner amendment — 2026-10-08: execution policy for portable browser

Status: APPROVED for continuation from the P106 licensing STOP. Earlier portable instructions to expose/test Visible or bundle a headed browser are superseded for Windows portable v1.0.0; they remain historical. Source/development continues to expose and validate both Background and Visible.

Before continuing P106, audit the exact Playwright 1.61.0 Background executable and accompanying licenses/notices. R14 does not pass automatically. If its redistribution basis cannot be demonstrated sufficiently, preserve the STOP for owner review; do not downgrade Playwright or substitute a browser. If R14 passes, bundle only Background-required assets, prove Chrome for Testing headed files absent, then complete R05–R07/R14–R16.

The shared packaged CLI reports Background without a Visible selector. P107 clean/isolated portable smoke, cancellation, console close, and R19 use the bundled Background path; source regression separately preserves Visible. P108 records the two capabilities, final source regression from the project `venv`, final RC ZIP and SHA-256, and two owner acceptance tracks. R20 stays OWNER_ACCEPTANCE_PENDING. Local commits are authorized; push, tag and public release (A3) are not.

## Owner amendment — 2026-10-08: Edge execution and gate procedure

Status: APPROVED for autonomous continuation from P106. Earlier portable browser-bundling and Background-only instructions are superseded for v1.0.0; retain them as historical evidence. The source and portable both offer Background (desired default) and Visible using installed Microsoft Edge Stable through Playwright `channel="msedge"`. Edge is an external prerequisite, not redistributed or automatically installed.

Before closing P106, repeat R04 with bounded Edge headed/headless live evidence, adapt BrowserRuntime and its controlled unavailable/blocked error, and test both mode paths. Remove browser-cache copying from the PyInstaller build. Inspect the actual artifact for absence of Chrome for Testing, Chrome Headless Shell, Chromium and Edge executables. R06 is **Browser Runtime Availability**; R14 applies to the remaining shipped dependencies and notices, not external Edge. R05/R07/R16 must be rerun on the amended artifact.

After P106 PASS, P107 requires legitimate clean/isolated Windows 10/11 x64 with Edge Stable but no repository, Python/venv or Playwright-managed browser cache, plus packaged live Background/Visible smoke, cancellation and console-close evidence. P108 then performs source regression from project `venv` using unique external `%TEMP%` basetemp, final contract/docs audit, RC ZIP and SHA-256, and owner Track A/B checklists. R20 remains OWNER_ACCEPTANCE_PENDING. No push, tag, GitHub Release, stable publication or A3 action.

## Owner operational exception — 2026-10-08: clean-machine gate

Do not execute or fabricate R08 on the present development host. For v1.0.0, record **R08 OWNER_WAIVED / DEFERRED_POST_RELEASE**, not PASS. The original clean-machine procedure remains above for historical traceability and future compatibility validation. A second clean Windows host is unavailable and Windows Sandbox is unavailable; relocated execution without Playwright browser-cache dependency on this host is supporting R07/R19 evidence only. The owner accepts environment-specific Windows/Edge/enterprise-policy residual risk, to be handled after release as maintenance/hardening.

The amended R19 consists of source regression plus final packaged-product smoke on the current host. P107 may pass with R08 waived only if R09 controlled cancellation, R10 best-effort console-close cleanup, packaged smoke and amended R19 pass. P108 then audits contracts, builds and hashes the owner-testable RC. Stop at R20 OWNER_ACCEPTANCE_PENDING. No push, tag, GitHub Release or A3 publication is authorized.

**END — V1-0-0-AUTONOMOUS-IMPLEMENTATION-RUNBOOK**

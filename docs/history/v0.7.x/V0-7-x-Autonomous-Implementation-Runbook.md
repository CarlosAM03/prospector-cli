# Prospector CLI — v0.7.x Autonomous Implementation Runbook

**Document type:** Engineering Execution Runbook  
**Version:** 1.0  
**Status:** APPROVED — AUTONOMOUS IMPLEMENTATION POLICY  
**Date:** 2026-10-04  
**Project:** Prospector CLI  
**Repository:** `CarlosAM03/prospector-cli`  
**Branch:** `main`  
**Expected baseline:** `ea7971b7bf3e4d3382debb6ee97c89f49b46bbd3`  
**Starting version:** `v0.7.0`  
**Target implementation line:** `v0.7.1` → `v0.7.7`  
**Execution model:** Continuous autonomous implementation  
**Human reviews between patches:** Not required under approved scope  
**Final acceptance:** Reserved for human review

---

# 1. Purpose

This document defines the operational rules under which Codex is authorized to plan, implement, test, correct, integrate and document the complete Prospector CLI `v0.7.x` stabilization line.

Its purpose is to reduce unnecessary interruptions while preserving architectural integrity, regression safety, data correctness and version boundaries.

Codex must aim to complete all seven approved patches in a continuous execution workflow.

Routine implementation decisions, test failures and minor internal refactors must be resolved autonomously.

Codex must not stop merely because an internal work package or patch has finished.

The authorized workflow is:

```text
Verify baseline
       |
       v
v0.7.1 — Google Maps Stability
       |
       v
v0.7.2 — EngineConfig
       |
       v
v0.7.3 — Browser Runtime
       |
       v
v0.7.4 — Logging
       |
       v
v0.7.5 — Error Model
       |
       v
v0.7.6 — ProspectorEngine
       |
       v
v0.7.7 — CLI Migration
       |
       v
Full regression and architecture audit
       |
       v
Final implementation report
       |
       v
Human acceptance
```

Internal checkpoints are mandatory, but ordinary human approvals between checkpoints are no longer required.

This policy supersedes the previous requirement for separate human implementation authorization after every work package.

It does not supersede architectural decisions, external-operation restrictions or final release acceptance requirements.

---

# 2. Authoritative documentation

Before modifying code, Codex must locate and read the following documents.

## 2.1 Master Plan

```text
temp/Planeacion/PlanMaestroV0.7.x.md
```

Defines:

- Seven approved patches.
- Version boundaries.
- Component ownership.
- Configuration responsibilities.
- Runtime responsibilities.
- Error semantics.
- Compatibility requirements.
- Release acceptance criteria.

## 2.2 Approved v0.7.1 documents

```text
temp/Planeacion/v0.7.1/
    V0-7-1-GoogleMaps-PlanningBrief.md
    V0-7-1-GoogleMaps-TechnicalDesign.md
    V0-7-1-GoogleMaps-TestMatrix.md
    V0-7-1-GoogleMaps-ExecutionPlan.md
    V0-7-1-GateB-DecisionRecord.md
```

The `v0.7.1` technical design and its decisions are already approved.

Codex must not independently redesign the patch.

## 2.3 Official documentation

Read the applicable files:

```text
README.md
docs/architecture.md
docs/roadmap.md
docs/scripting-pipeline.md
docs/pipelines/google_maps.md
docs/contributing.md
tests/README.md
```

## 2.4 Audit evidence

Review relevant material from:

```text
temp/audits/
temp/HANDOFFs/
```

Historical audits provide evidence and context.

They must not override current source code, permanent tests or approved architectural decisions.

## 2.5 Authority hierarchy

For approved direction:

```text
Approved Master Plan
       |
Approved Decision Records
       |
Approved Patch Technical Design
       |
This Execution Runbook
       |
Official Roadmap
       |
Implementation details
```

The Runbook governs execution mechanics and autonomy.

It cannot authorize functionality prohibited by the Master Plan.

For existing behavior, current source code and permanent tests are primary evidence.

---

# 3. Repository baseline verification

Before implementation, execute:

```powershell
git branch --show-current
git rev-parse HEAD
git status --short
git log -5 --oneline
```

Expected baseline:

```text
ea7971b7bf3e4d3382debb6ee97c89f49b46bbd3
```

Record:

- Actual HEAD.
- Current branch.
- Working-tree status.
- Uncommitted modifications.
- Existing untracked or ignored planning files.
- Current test status.

Do not assume that the baseline remains unchanged.

If HEAD differs, determine whether subsequent changes are compatible with the approved plans.

Do not overwrite unrelated user modifications.

If an unexpected change threatens data preservation or architectural compatibility, isolate the conflict rather than forcing a reset.

Do not use destructive Git operations without explicit authorization.

---

# 4. Autonomous execution authorization

Codex is authorized to:

1. Inspect the repository.
2. Design internal implementation details.
3. Modify production code within approved patch scopes.
4. Add deterministic unit tests.
5. Add controlled integration tests.
6. Improve relevant test fixtures.
7. Execute offline regression tests.
8. Diagnose and correct implementation failures.
9. Refactor code when necessary to satisfy approved contracts.
10. Introduce small internal helpers when justified.
11. Calibrate internal timeouts and attempt budgets.
12. Update official documentation to reflect verified implementation.
13. Document remaining limitations.
14. Produce local implementation reports.
15. Create reviewable local Git checkpoints for completed, validated patches when repository state permits.
16. Continue automatically to subsequent approved patches.

Codex must not request human permission for routine changes already covered by this authorization.

## 4.1 Explicit prohibitions

Without separate authorization, Codex must not:

- Push to a remote.
- Open or merge pull requests.
- Publish releases.
- Create release tags.
- Modify repository visibility or licensing.
- Delete user data.
- Reset or clean unrelated working-tree content.
- Install new dependencies unnecessarily.
- Introduce paid API or membership features.
- Implement a SaaS application.
- Introduce new prospect sources.
- Implement normalization before `v0.8.x`.
- Implement multi-input or business deduplication before `v0.9.x`.
- Physically separate the Engine into another package.
- Implement browser pooling or concurrency.
- Introduce a general job orchestration framework.
- Run live Google Maps scraping without explicit batch authorization.
- Run external performance benchmarks without approval.
- Silently change approved public contracts.
- Fabricate test outcomes, benchmarks or approval decisions.

---

# 5. Continuous execution policy

The primary operational objective is:

**Complete as much of the approved `v0.7.x` line as safely possible without ordinary human interruptions.**

Codex must independently handle:

- Routine implementation choices.
- Internal module organization.
- Test fixture design.
- Failing unit tests.
- Controlled integration failures.
- Small refactors.
- Internal naming decisions.
- Documentation updates.
- Patch-local regressions.

Human intervention is reserved for decisions that materially affect approved architecture or require separate external authorization.

## 5.1 Patch checkpoint

After every patch:

1. Run focused tests.
2. Run the complete default regression suite.
3. Review the implementation diff.
4. Check architectural scope.
5. Review compatibility.
6. Record actual test outcomes.
7. Update current documentation.
8. Record unresolved issues.
9. Create a local checkpoint if all required conditions are satisfied.
10. Continue to the next patch.

Do not treat completing a patch checkpoint as a reason to stop execution.

## 5.2 Failed validation

If a newly introduced regression occurs:

1. Identify the failing invariant.
2. Reproduce the failure.
3. Correct the relevant implementation.
4. Rerun affected tests.
5. Rerun required regression coverage.
6. Continue after validation succeeds.

Do not bypass failing tests by weakening assertions that protect approved behavior.

Do not mark a patch validated while known critical regressions remain.

## 5.3 Unresolved blockers

Classify blockers as:

```text
IMPLEMENTATION_BLOCKER
ARCHITECTURAL_DECISION_REQUIRED
EXTERNAL_AUTHORIZATION_REQUIRED
ENVIRONMENT_BLOCKER
EXTERNAL_SOURCE_VARIABILITY
```

If a blocker is local to one patch:

- Preserve a compatible working state.
- Document the blocker.
- Continue independent work when safe.
- Return to the blocked requirement if new evidence becomes available.

If the blocker prevents a later contract from being finalized:

- Do not fabricate the missing contract.
- Do not declare the dependent patch approved.
- Continue only work that can remain contract-neutral.
- Avoid stacking implementations on unresolved assumptions.

If no further independent, safe work is possible, stop and report the precise blocking decision.

---

# 6. Global architectural invariants

The following contracts apply to every patch.

## 6.1 Domain

- Preserve `SearchQuery` semantics.
- Preserve `Business` field compatibility.
- Preserve valid extracted information.
- Preserve Business ordering.
- Preserve `SearchResult.total_found` as the number of returned Businesses.
- Avoid associating one Business with another Business's information.

## 6.2 Extraction

- Source-specific extraction remains source-specific.
- Reusable infrastructure stays independent of Google Maps-specific assumptions.
- Partial optional-enrichment failures must not erase valid data.
- External DOM variability must not be treated as deterministic behavior.

## 6.3 Export

- `ExportService` remains outside `ProspectorEngine`.
- CSV/XLSX behavior and existing schema remain compatible.
- `output_path` remains outside `EngineConfig`.

## 6.4 Execution

- Browser resources must have clear ownership.
- Owned resources must be released.
- No unrelated cross-query mutable state.
- No persistent browser pooling.
- No new concurrency model.

## 6.5 Version boundaries

```text
v0.7.x: Stability and architecture
v0.8.x: Normalization
v0.9.x: Multi-input and deduplication
v1.0.0: Stable extraction-ready release
Post-v1: Possible physical Engine separation
```

---

# 7. v0.7.1 — Google Maps Stability

**Scope:** Approved  
**Detailed design:** Approved  
**Execution authorization:** Granted under this Runbook

Implement the approved `v0.7.1` Technical Design and Execution Plan.

The implementation must follow:

```text
GM-02 — Navigation and readiness
GM-03 — Virtual result loading
GM-04 — Detail-panel identity
GM-05 — Partial-result preservation
GM-06 — Validation
```

GM-01 has already been completed through the read-only audit.

## 7.1 Approved changes

| Change | Responsibility |
|---|---|
| C01 | Navigation/readiness |
| C02 | Delayed semantic selectors |
| C03 | Incremental result collection |
| C04 | Detail identity |
| C05 | Generic wait boundaries |
| C06 | Safe website metadata merge |
| C07 | Minimal exceptional browser cleanup |

## 7.2 Mandatory decisions

Apply:

```text
H01–H07 = APPROVED
P-01 = APPROVED
P-02 = APPROVED
```

Specifically:

- Preserve legacy `limit <= 0` behavior.
- Return valid partial Businesses on bounded feed stalls.
- Require verifiable empty-state evidence.
- Track source candidates without business deduplication.
- Separate useful feed progress from UI activity.
- Require strong detail identity validation.
- Preserve summary data when identity is uncertain.
- Use only approved name equivalence.
- Allow local `finally` cleanup without introducing Browser Runtime.

## 7.3 Required tests

Implement the approved Test Matrix:

```text
T-N01–T-N06
T-S01
T-F01–T-F14
T-D01–T-D10
T-W01–T-W04
T-I01–T-I06
```

Total planned scenarios: 41.

Tests must remain deterministic unless explicitly classified as live E2E.

Use controlled fake states to reproduce navigation delays, feed virtualization, stale panels, identity mismatches and partial failures.

## 7.4 Acceptance

The patch is implemented when:

- Readiness is meaningful and bounded.
- Feed progress and termination are bounded.
- Business order and requested positive limits remain correct.
- Legacy nonpositive limits are preserved.
- No unverified detail information is assigned.
- Optional failures preserve valid data.
- Browser cleanup behaves correctly.
- New controlled tests pass.
- Existing regression tests pass.

Do not declare the live Google Maps E2E passed unless an authorized run actually occurs.

Record external validation as not executed when approval is unavailable.

Do not invent an `engine_max_limit`.

---

# 8. v0.7.2 — EngineConfig Boundary

**Scope:** Approved by Master Plan  
**Implementation:** Autonomous within approved boundaries

## 8.1 Objective

Introduce minimal typed configuration for the reusable extraction pipeline.

## 8.2 Required configuration concepts

```text
limit
headless
website_enrichment
```

Keep the following distinct:

```text
requested_limit
default_limit
engine_max_limit
```

The requested limit must be configurable by the consumer.

The operational maximum belongs to the Engine policy.

A future API consumer may impose membership quotas separately.

Commercial quotas must not be implemented in Prospector CLI.

## 8.3 Validation behavior

Approved rules:

- Positive requested limit required under the new contract.
- Requested limit cannot exceed Engine maximum.
- Invalid requests must be rejected explicitly.
- No silent clamping.
- No unbounded requests.
- Typed and predictable configuration.
- No unnecessary public low-level timing options.

Preserve legacy entrypoint behavior through the approved compatibility strategy.

Do not retroactively rewrite historical `v0.7.1` behavior.

## 8.4 Deferred Engine maximum

The numerical value of `engine_max_limit` remains subject to performance and stability evidence.

Codex may autonomously:

- Implement a configurable internal validation mechanism.
- Test it with controlled numerical values.
- Produce capacity analysis.
- Recommend a maximum based on existing authorized evidence.
- Document tradeoffs.

Codex must not:

- Treat 500 as a proven Engine maximum.
- Invent benchmark results.
- Run unauthorized live measurements.
- Present an unapproved number as final policy.

If no approved maximum is available, mark the policy decision unresolved.

Continue contract-neutral work where possible.

Do not claim that `v0.7.2` is fully approved or release-ready until the maximum policy has been resolved as required by the Master Plan.

## 8.5 Acceptance

- Config construction and validation tested.
- Consumer requested limits supported.
- Default behavior preserved where approved.
- Headless setting represented correctly.
- Website enrichment setting represented correctly.
- No CLI/export responsibilities inside EngineConfig.
- No uncontrolled public configuration expansion.
- Regression suite green.

---

# 9. v0.7.3 — Browser Runtime

**Scope:** Approved by Master Plan

## 9.1 Objective

Establish dedicated ownership of browser resources for each extraction execution.

## 9.2 Required behavior

- Acquire Playwright resources.
- Launch Chromium when needed.
- Establish browser/context/page ownership.
- Provide resources to consumers without transferring ownership implicitly.
- Release owned resources.
- Guarantee cleanup on normal execution.
- Guarantee cleanup on exceptions.
- Preserve fatal exception propagation.
- Avoid double close.

The Runtime must consume the approved `headless` configuration.

## 9.3 Architecture

The Runtime is internal execution infrastructure.

Google Maps navigation remains responsible for source behavior.

Website inspection retains its own appropriate resource boundaries or adopts shared resources only when ownership is explicit and tested.

Avoid requiring every future data source to use Playwright.

## 9.4 Restrictions

No:

- Browser pooling.
- Parallel execution.
- Multiple concurrent queries.
- Remote browser service.
- Persistent jobs.
- Global mutable browser singleton.
- Distributed execution.

## 9.5 Acceptance

Controlled tests must cover:

- Normal cleanup.
- Fatal navigation failure.
- Recoverable enrichment failure.
- Browser startup failure.
- Nested page/context cleanup.
- Single ownership.
- No double close.
- Exception preservation.

The existing local `finally` from `v0.7.1` may be replaced or integrated when ownership is safely transferred to the Runtime.

Regression suite must remain green.

---

# 10. v0.7.4 — Logging Boundary

**Scope:** Approved by Master Plan

## 10.1 Objective

Separate internal diagnostics from interactive presentation.

## 10.2 Required behavior

Use standard Python logging.

Ensure:

- Module-appropriate loggers.
- Suitable diagnostic levels.
- Relevant execution context.
- No reliance on `print` for internal diagnostics.
- No unexpected root-logger configuration.
- No leakage of user-facing output responsibility into the extraction core.

## 10.3 Restrictions

Do not introduce:

- Third-party telemetry platforms.
- Distributed tracing.
- Centralized logging services.
- Remote analytics.
- Audit databases.
- Public log profile systems without approval.

## 10.4 Acceptance

- Internal diagnostics use logging.
- CLI messages remain user-facing.
- Tests verify diagnostic behavior where relevant.
- No data extraction semantics are changed.
- Logging does not become an error contract.
- Regression suite green.

---

# 11. v0.7.5 — Error Model

**Scope:** General semantics approved  
**Exact schema:** Requires human ratification before becoming final

## 11.1 Objective

Introduce structured recoverable failures and typed fatal errors.

## 11.2 Approved semantics

Recoverable failures:

```text
Preserve valid Business data.
Record a structured issue.
Continue when safely possible.
```

Fatal failures:

```text
Stop the affected extraction.
Release owned resources.
Raise a typed exception.
```

`SearchResult` may be extended with a backward-compatible issue collection.

The exact schema must respect approved model compatibility.

## 11.3 Design autonomy

Codex may:

- Analyze existing failure modes.
- Design a minimal issue schema.
- Design an exception hierarchy.
- Implement provisional internal adapters where compatible.
- Add controlled tests.
- Document compatibility implications.

Codex must not claim human approval of an unratified public schema.

Avoid introducing a large generalized error framework.

## 11.4 Required invariants

- Existing Businesses remain ordered.
- `total_found` counts Businesses, not issues.
- CSV/XLSX schema remains compatible.
- Recoverable failures preserve valid fields.
- Fatal failures propagate predictably.
- Logging remains diagnostic only.
- Browser Runtime cleanup remains guaranteed.

## 11.5 Blocking decision

If the exact issue schema and exception hierarchy have not received human approval, do not freeze them as stable public contracts.

Codex may continue unrelated implementation work.

It must not finalize dependent public Engine behavior using an invented contract.

## 11.6 Acceptance

- Approved or clearly provisional issue representation.
- Typed fatal categories.
- Recoverable data preservation.
- Controlled propagation.
- No silent data corruption.
- Full regression suite green.
- Final contract status explicitly reported.

---

# 12. v0.7.6 — ProspectorEngine Facade

**Scope:** Approved by Master Plan

## 12.1 Objective

Introduce the reusable internal extraction entrypoint.

Approved conceptual contract:

```python
ProspectorEngine(config).search(query) -> SearchResult
```

## 12.2 Required behavior

- Consume `EngineConfig`.
- Delegate source-specific extraction.
- Use the Browser Runtime.
- Return `SearchResult`.
- Apply approved error semantics.
- Remain independent from CLI presentation.
- Remain independent from export/output management.

## 12.3 Compatibility

The facade must not modify:

- Business ordering.
- SearchQuery semantics.
- Domain identity.
- ExportService ownership.
- Current source behavior without justified evidence.

The existing Google Maps source remains the implemented strategy.

No speculative multi-source registry or public plugin API is required.

## 12.4 Dependency restrictions

If `engine_max_limit` or the public Error Model schema is still awaiting human approval:

- Implement only contract-neutral orchestration when safe.
- Clearly mark integrations dependent on provisional contracts.
- Avoid publishing or declaring those contracts stable.
- Do not hide unresolved dependencies through arbitrary defaults.

## 12.5 Acceptance

- Engine constructed using approved configuration.
- Search returns the expected SearchResult.
- No interactive input inside Engine.
- No CSV/XLSX export inside Engine.
- Source delegation tested.
- Error behavior consistent with approved contracts.
- Controlled integration suite green.

---

# 13. v0.7.7 — CLI Migration & Closure

**Scope:** Approved by Master Plan

## 13.1 Objective

Migrate the interactive CLI to the reusable `ProspectorEngine` boundary.

## 13.2 Required behavior

The CLI must:

1. Collect search keywords/location.
2. Accept an optional requested limit.
3. Apply the appropriate default.
4. Validate requested input.
5. Construct Engine configuration.
6. Execute a search through `ProspectorEngine`.
7. Present results.
8. Present errors appropriately.
9. Export through existing ExportService when requested.

## 13.3 Transitional compatibility

Preserve:

```python
search_businesses(query, limit=50)
```

through the approved wrapper strategy.

Avoid maintaining duplicate implementations.

The CLI must not orchestrate Google Maps-specific extraction details.

## 13.4 Export compatibility

Existing CSV/XLSX formats and Business field mappings remain compatible.

The Engine must not absorb ExportService.

## 13.5 Restrictions

No:

- Full CLI redesign.
- New API.
- Membership system.
- Batch mode.
- Multiple-input execution.
- Deduplication.
- Normalization.
- New source plugins.

## 13.6 Acceptance

- CLI invokes ProspectorEngine.
- Search executes correctly through controlled integration.
- Limit input/default behavior verified.
- Fatal and recoverable failures handled appropriately.
- Export behavior preserved.
- Legacy wrapper tested.
- Documentation reflects implemented architecture.
- Full default regression suite green.

---

# 14. Automatic quality gates

The following gates apply across the complete execution.

## QG-01 — Source validation

Before each modification:

- Identify owning module.
- Identify affected contract.
- Identify expected regression risk.
- Define validation evidence.

## QG-02 — Focused tests

After each meaningful change:

- Run related unit tests.
- Run controlled integration tests as applicable.
- Correct new regressions.

## QG-03 — Full regression

At each patch checkpoint, execute:

```powershell
python -m compileall -q src
python -m pytest -q
git diff --check
git status --short
```

Record:

- Exact command.
- Exit status.
- Passed tests.
- Failed tests.
- Deselected tests.
- Environment limitations.

Do not claim a test passed without running it.

## QG-04 — Scope audit

Inspect the actual diff.

Verify:

- No future-version work.
- No unauthorized dependency.
- No accidental model/schema changes.
- No export contract change.
- No unrelated modifications.
- No source-specific coupling introduced into shared infrastructure.

## QG-05 — Compatibility audit

Verify:

- Existing public entrypoints.
- Existing model construction.
- Default behavior.
- Business order.
- Partial-result preservation.
- Export semantics.

## QG-06 — Documentation audit

Update applicable official documentation after implemented behavior is verified.

Do not document TARGET behavior as CURRENT.

## QG-07 — Final integration

After v0.7.7, run the complete deterministic suite and examine all seven implementation areas together.

If dependencies remain unresolved, report the final state accurately instead of claiming release completion.

---

# 15. Live E2E and capacity measurement policy

Live Google Maps validation remains opt-in.

No general authorization to execute live scraping is granted by this Runbook.

H07 requires separate authorization for each live batch.

Before a live batch, document:

- Query categories.
- Exact query/region set.
- Requested limits.
- Repetition count.
- Time budget.
- Stop conditions.
- Evidence collection.
- Operational risks.

Do not run a batch without approval.

A live test not executed must be reported as:

```text
NOT EXECUTED — AUTHORIZATION REQUIRED
```

A single successful live search is not evidence of an Engine maximum.

Capacity experiments must distinguish requested limit, valid returned Businesses, source availability and processing cost.

---

# 16. Git checkpoint policy

Codex may create local commits only for completed and validated implementation checkpoints, provided the repository has no conflicting unrelated changes.

Before each checkpoint:

1. Inspect `git status`.
2. Inspect staged and unstaged diffs.
3. Verify test outcomes.
4. Verify documentation.
5. Confirm the files belong to the approved patch.
6. Stage only owned files.
7. Create a descriptive local commit.

Suggested messages:

```text
fix(maps): stabilize navigation and extraction
refactor(engine): introduce minimal configuration
refactor(runtime): establish browser lifecycle
refactor(logging): separate internal diagnostics
feat(errors): introduce structured error semantics
feat(engine): add reusable extraction facade
refactor(cli): migrate to prospector engine
```

These are suggestions, not mandatory wording.

Do not create an approved release tag automatically.

Do not push.

Do not modify remote branches.

Do not amend historical commits.

Do not use `git reset --hard`, broad `git clean`, force-push or equivalent destructive commands.

If a patch remains provisional or has unresolved critical regressions, do not represent its checkpoint as a completed stable release.

---

# 17. Local implementation reporting

Record progress under:

```text
temp/Planeacion/v0.7.x/
```

Suggested internal reports:

```text
ImplementationProgress.md
ImplementationBlockers.md
ValidationMatrix.md
FinalArchitectureAudit.md
```

These files are local implementation evidence.

They must not replace permanent tests or official documentation.

Progress reports must distinguish:

```text
NOT_STARTED
IN_PROGRESS
IMPLEMENTED
VALIDATED
PROVISIONAL
BLOCKED
HUMAN_APPROVAL_REQUIRED
```

The implementation state and release approval state are separate.

Codex must maintain enough traceability to explain what has actually changed.

---

# 18. Autonomous recovery rules

## 18.1 Test failure

Correct and rerun.

Do not skip tests solely to pass a checkpoint.

## 18.2 Unexpected source behavior

Investigate controlled reproduction.

Do not fabricate Google Maps selectors or behavior.

## 18.3 Missing local dependencies

Check existing development instructions.

Do not introduce permanent dependency changes merely to repair an environment problem.

## 18.4 Architectural contradiction

Stop modifications that depend on the contradiction.

Document the evidence, alternatives and impact.

Continue independent work when safe.

## 18.5 Unapproved public contract

Do not finalize or publish the contract.

Implement only compatible independent components.

Record the required human decision.

## 18.6 External authorization required

Do not execute the external operation.

Proceed with controlled offline tests.

Record the missing validation evidence.

---

# 19. Final v0.7.x architecture audit

After attempting all seven patches, evaluate:

## Google Maps

- Correct readiness.
- Bounded scrolling.
- Identity-safe detail extraction.
- Partial-data preservation.

## Configuration

- Requested/default/maximum semantics.
- Typed validation.
- Minimal public configuration.

## Runtime

- Clear resource ownership.
- Cleanup on success/failure.
- No double close.
- No pooling.

## Logging

- Diagnostics isolated.
- CLI presentation independent.

## Errors

- Recoverable issues.
- Typed fatal exceptions.
- Valid partial results retained.

## Engine

- Reusable facade.
- No CLI/export dependency.
- Correct source delegation.

## CLI

- Engine-based execution.
- Configurable limit input.
- Existing export behavior.
- Transitional compatibility.

## Version boundaries

Verify that `v0.8.x`, `v0.9.x` and post-v1 functionality has not been introduced.

---

# 20. Final report requirements

At the end of the execution, produce:

```text
PROSPECTOR CLI v0.7.x
AUTONOMOUS IMPLEMENTATION REPORT
================================

Initial HEAD:
Final HEAD:
Branch:
Working-tree status:

PATCH STATUS
------------
v0.7.1:
v0.7.2:
v0.7.3:
v0.7.4:
v0.7.5:
v0.7.6:
v0.7.7:

IMPLEMENTED COMPONENTS
----------------------

TEST EVIDENCE
-------------
Unit:
Integration:
Default regression:
Live E2E:
Capacity measurements:

COMPATIBILITY
-------------

ARCHITECTURAL AUDIT
-------------------

DEFERRED CONTRACTS
------------------
engine_max_limit:
Error Model schema:
Other decisions:

DOCUMENTATION
-------------

LOCAL COMMITS
-------------

UNRESOLVED FAILURES
-------------------

REQUIRES HUMAN APPROVAL
-----------------------

FINAL STATUS
------------
IMPLEMENTED / PROVISIONAL / BLOCKED
```

The report must distinguish implementation completion from official release acceptance.

Do not present an incomplete or provisional implementation as approved.

---

# 21. Definition of Done

The autonomous task reaches its strongest completion state when:

- All seven patches are implemented.
- Required deterministic tests pass.
- No newly introduced critical regression remains.
- Approved compatibility contracts are preserved.
- Relevant official documentation is accurate.
- Architecture boundaries remain intact.
- No unauthorized external operation was performed.
- Any deferred contract received required approval.
- Final implementation evidence is complete.
- The resulting code is ready for human release acceptance.

If one or more mandatory human decisions remain unresolved, the task may finish with a provisional implementation report, but it must not claim that the entire `v0.7.x` line is release-ready.

---

# 22. Operational directive

Codex is authorized to execute the seven patches continuously within this Runbook.

**Do not stop after ordinary internal checkpoints.**

**Do not ask for routine implementation approvals.**

**Do not weaken tests or violate architectural boundaries to maintain progress.**

**Do not invent missing policy decisions.**

**Do not execute unauthorized external operations.**

**Do not push, tag or publish.**

When a genuine blocker appears, complete independent safe work and record the limitation precisely.

Continue until all approved implementation work is complete or no further safe progress is possible.

The final output must be an evidence-based implementation report suitable for human acceptance.

**End of Autonomous Implementation Runbook v1.0.**
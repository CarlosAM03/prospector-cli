# Prospector CLI — v0.7.x Implementation Master Plan

**Document type:** Engineering Implementation Master Plan  
**Version:** 1.0  
**Status:** APPROVED  
**Approval date:** 2026-10-04  
**Project:** Prospector CLI  
**Repository:** `CarlosAM03/prospector-cli`  
**Branch:** `main`  
**Planning baseline:** `ea7971b7bf3e4d3382debb6ee97c89f49b46bbd3`  
**Current application version:** `v0.7.0`  
**Target line:** `v0.7.1` → `v0.7.7`  
**Implementation status:** NOT STARTED

---

# 1. Purpose

This document defines the approved implementation scope, architectural constraints, dependencies, acceptance criteria, and release structure required to complete the `v0.7.x` stabilization line of Prospector CLI.

The purpose of `v0.7.x` is to establish a stable and reusable internal extraction architecture before introducing deterministic normalization in `v0.8.x`.

The implementation line must:

- Preserve existing functional behavior.
- Stabilize Google Maps extraction.
- Establish explicit configuration boundaries.
- Separate browser lifecycle ownership from source-specific extraction.
- Separate internal diagnostics from CLI presentation.
- Introduce structured error and partial-result semantics.
- Introduce the internal `ProspectorEngine` facade.
- Migrate the interactive CLI to the new Engine boundary.
- Preserve the reusable export infrastructure.
- Maintain regression safety throughout the transition.

This plan does not redefine the identity, philosophy, or long-term purpose of Prospector CLI.

It refines the implementation path toward the previously approved `v1.0.0` objectives.

## 1.1 Approval meaning

`APPROVED` means that the overall implementation strategy, seven-patch decomposition, ownership principles, version boundaries, and documented architectural decisions have received human approval.

Approval does not mean that every low-level implementation detail has been selected.

Individual patches may still require:

- Detailed technical design.
- Explicit acceptance tests.
- Evidence-based parameter selection.
- Approval of deferred technical contracts.
- Implementation instructions for Codex.

The Master Plan is therefore approved as the controlling implementation plan, while patch-level execution remains subject to its corresponding review and acceptance gates.

---

# 2. Project identity and architectural principles

Prospector CLI is an independent open-source Python command-line project designed to extract structured business/prospect information from public data sources.

The project prioritizes:

- Simplicity.
- Single responsibility.
- Modularity.
- Reusability.
- Readability.
- Source-specific extraction strategies.
- Incremental enrichment.
- Clear dependency direction.
- Separation of extraction, presentation, and export.
- Configuration over hardcoded behavior where appropriate.
- Extensibility without premature generalization.

The project is currently CLI-first.

The internal architecture should support future Python consumers without coupling the extraction core to its current interactive interface.

Possible future consumers may include APIs or other applications. Such consumers do not form part of the current Prospector CLI implementation scope.

## 2.1 Architectural ownership principles

Reusable execution infrastructure belongs in appropriately shared components.

Source-specific extraction behavior remains inside the corresponding source pipeline.

Utilities provide focused reusable operations.

A component does not become source-specific merely because only one source currently consumes it.

Likewise, a component must not be generalized prematurely merely because future reuse is theoretically possible.

## 2.2 Project independence

Prospector CLI must not become:

- A SaaS platform.
- An HTTP API.
- A CRM or ERP.
- A private consumer backend.
- A marketing campaign management system.
- A job execution service.
- A distributed scraping platform.
- A subscription or membership management service.

The possible development of these systems by external consumers does not modify the responsibilities of this repository.

---

# 3. Baseline and current implementation

The authoritative baseline is:

`ea7971b7bf3e4d3382debb6ee97c89f49b46bbd3`

The baseline incorporates:

1. Phase 0 — Current Code Audit.
2. Phase 1 — Regression Safety.
3. Documentation Reconciliation.
4. Open-Source Identity Restoration.
5. Historical Knowledge Classification.

The temporary audit corpus contains the original evidence and planning inputs.

These materials are supporting evidence, not substitutes for current source code and permanent tests.

## 3.1 Current extraction flow

```text
Interactive CLI
      |
      v
SearchQuery
      |
      v
search_businesses(query, limit)
      |
      v
Playwright / Chromium
      |
      v
NavigationEngine
      |
      v
GoogleMapsNavigation
      |
      v
Google Maps result feed
      |
      v
Virtual/infinite scrolling
      |
      v
Summary extraction
      |
      v
Business[]
      |
      v
Detail-panel enrichment
      |
      v
Website Engine enrichment
      |
      v
SearchResult
      |
      +--> CLI presentation
      |
      +--> ExportService
               |
             CSV/XLSX
```

The current programmatic boundary is:

```python
search_businesses(
    query: SearchQuery,
    limit: int = 50,
) -> SearchResult
```

The interactive CLI currently calls this function using `limit=500`.

These values represent current behavior and do not establish the future maximum capacity of the Engine.

## 3.2 Current limitations

The implementation currently contains:

- Embedded Playwright/browser lifecycle.
- Hardcoded browser visibility.
- Source-specific synchronization waits.
- Fixed scrolling parameters.
- Distributed feed loading responsibility.
- Internal diagnostic `print` calls.
- Heterogeneous exception handling.
- Broad exception catches.
- Silent recovery in some enrichment paths.
- No structured partial-result issue representation.
- No `EngineConfig`.
- No `ProspectorEngine`.
- No formal normalization layer.
- No multi-input or deduplication layer.

The `v0.7.x` plan addresses only the architectural and stability concerns assigned to this version line.

---

# 4. Approved version boundaries

The following version boundaries are normative.

| Version | Primary responsibility |
|---|---|
| `v0.7.x` | Stability and architectural decoupling |
| `v0.8.x` | Formal deterministic normalization |
| `v0.9.x` | Multi-input and deduplication |
| `v1.0.0` | First complete/stable extraction-ready release |
| Post-v1 | Possible physical Engine extraction and additional extensions |

## 4.1 v0.7.x exit objective

The line must leave a sufficiently stable architectural foundation for `v0.8.x` to concentrate on normalization.

Structural problems belonging to the seven approved concerns must not be silently deferred to `v0.8.x`.

## 4.2 v0.8.x

Normalization is explicitly outside `v0.7.x`.

`v0.8.x` will define and implement deterministic normalization behavior and its corresponding invariants.

## 4.3 v0.9.x

The approved core scope is:

- Multiple search inputs.
- Deduplication.

Merge, batch execution, browser reuse, concurrency, identity confidence, and query-level partial-result semantics require later design decisions.

## 4.4 v1.0.0

The first stable release must provide stable CLI behavior, reusable internal contracts, regression safety, documented configuration and error semantics, and an extraction-ready architecture.

Physical extraction of a separate Prospector Engine package is not required.

## 4.5 Post-v1

Possible future work includes:

- Separate Prospector Engine packaging.
- Additional source adapters.
- Additional output formats.
- Plugin infrastructure.
- Additional application consumers.
- More advanced execution strategies.

These possibilities do not extend the scope of `v0.7.x`.

---

# 5. Approved patch decomposition

The `v0.7.x` implementation line consists of seven incremental patch releases.

| Patch | Name | Main responsibility |
|---|---|---|
| `v0.7.1` | Google Maps Stability | Stabilize the existing source pipeline |
| `v0.7.2` | EngineConfig Boundary | Define minimal configuration and limit policy |
| `v0.7.3` | Browser Runtime | Establish resource ownership and cleanup |
| `v0.7.4` | Logging Boundary | Separate diagnostics from presentation |
| `v0.7.5` | Error Model | Structured recoverable/fatal error semantics |
| `v0.7.6` | ProspectorEngine Facade | Establish the internal reusable Engine |
| `v0.7.7` | CLI Migration & Closure | Complete integration and architectural stabilization |

Every patch must be individually testable, reviewable, and documented.

Patch numbers must not be reassigned without explicit approval of a Master Plan revision.

---

# 6. Dependency analysis

Not all relationships between concerns represent strict technical dependencies.

The plan distinguishes:

- **HARD DEPENDENCY:** a contract or component cannot be completed correctly without its prerequisite.
- **DESIGN DEPENDENCY:** interfaces must be compatible even when implementation can happen independently.
- **ORDERING PREFERENCE:** sequencing reduces risk but is not technically mandatory.

| Dependency | Classification | Rationale |
|---|---|---|
| Regression Safety → Maps Stability | HARD | Existing behavior must be protected before changes |
| Maps Stability → Configuration | ORDERING | Stabilization reduces uncertainty in the configured pipeline |
| EngineConfig ↔ Browser Runtime | DESIGN | `headless` requires a runtime consumer |
| Browser Runtime → Logging | ORDERING | Explicit runtime ownership simplifies diagnostics |
| Logging → Error Model | ORDERING | Diagnostics must remain separate from structured outcomes |
| Error Model → Stable Engine contract | HARD | The Engine must expose defined partial/fatal semantics |
| EngineConfig → Engine facade | HARD | The facade consumes approved configuration |
| Runtime → Engine facade | HARD | Execution ownership must be defined |
| Engine facade → CLI Migration | HARD | The CLI needs a functional Engine entrypoint |

## 6.1 Approved implementation sequence

```text
Regression Safety
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
v0.7.x Closure
      |
      v
v0.8.x Normalization
```

The interfaces between configuration and runtime must be designed together before introducing incompatible implementation assumptions.

---

# 7. Approved Architectural Decision Register

All decisions D-01 through D-08 have been explicitly approved.

## D-01 — Requested limit and Engine maximum

**Decision: A — APPROVED**

Distinguish:

1. Requested limit.
2. Default requested limit.
3. Maximum Engine limit.

The consumer can request a number of Businesses.

The Engine imposes an independent operational maximum.

The consumer-requested limit must never exceed that maximum.

Conceptually:

```text
1 <= effective_limit <= engine_max_limit
```

Where:

```text
effective_limit =
    explicit requested_limit
    OR
    default_limit
```

`EngineConfig.limit` represents the configured requested-limit default.

The exact Python signature and parameter placement will be finalized in the corresponding technical design, without introducing redundant public configuration surfaces.

### API-consumer separation

A future API may impose:

- Membership limits.
- User quotas.
- Request quotas.
- Commercial plan restrictions.

Those rules are outside Prospector CLI.

The Engine maximum is a technical capacity policy, not a membership or commercial authorization policy.

---

## D-02 — Requests above maximum

**Decision: A — APPROVED**

Requests exceeding the maximum must be rejected explicitly.

The Engine must not silently clamp the requested value.

The error must communicate the invalid request and the applicable limit through the approved error/configuration contract.

### Deferred numerical decision

The value of `engine_max_limit` has NOT been approved.

It must be informed by stability and performance evidence gathered during `v0.7.1`.

Its final value must be approved before closing `v0.7.2`.

The existing CLI request of 500 Businesses is not, by itself, evidence that 500 should be the maximum.

---

## D-03 — CLI limit input

**Decision: A — APPROVED**

The interactive CLI must allow users to enter a requested limit.

If no value is entered, a default is applied.

The input must be validated against the Engine maximum.

The final interactive integration belongs to `v0.7.7`.

### Compatibility requirement

The current CLI uses `limit=500`.

The current programmatic boundary defaults to 50.

These are distinct current behaviors.

They must not be silently unified or changed during early stabilization.

If the approved Engine maximum conflicts with the historical CLI default, the compatibility implications must be reviewed before changing CLI behavior.

---

## D-04 — Browser lifecycle ownership

**Decision: A — APPROVED**

Use a dedicated internal runtime component.

The runtime owns Playwright/browser resources for a single execution.

Consumers receive access to the resources needed for their respective operations.

The source pipeline must not independently assume responsibility for closing resources that it does not own.

Cleanup must be guaranteed for:

- Successful execution.
- Recoverable errors.
- Fatal extraction errors.
- Navigation failures.
- Unexpected exceptions.

The target excludes:

- Persistent browser pooling.
- Reuse between unrelated searches.
- Parallel execution.
- Distributed lifecycle management.
- Job management.

Browser ownership and acquisition strategy must not force every future source to use Playwright.

---

## D-05 — Error and partial-result semantics

**Decision: A — APPROVED**

Recoverable failures are represented through structured issues associated with `SearchResult`.

Fatal failures use typed exceptions.

Valid previously extracted Businesses must survive recoverable detail or website enrichment failures.

The initial conceptual model is:

```python
SearchResult(
    query=query,
    businesses=businesses,
    execution_time=elapsed,
    issues=[],
)
```

`issues` must not modify:

- Business ordering.
- Valid extracted fields.
- `total_found`.
- ExportService ownership.
- The established CSV/XLSX schema.

The final structure of each issue and the typed exception hierarchy remain deferred to the technical design of `v0.7.5`.

The implementation must not treat logging output as a substitute for structured issues.

---

## D-06 — Minimal EngineConfig and logging

**Decision: A — APPROVED**

The initial Engine configuration concerns are:

```text
limit
headless
website_enrichment
```

The maximum limit is an independent Engine policy.

Low-level values such as:

- Timeouts.
- Scroll distance.
- Stable cycles.
- Internal selector waits.
- Synchronization implementation details.

remain internal unless an additional architectural decision explicitly approves exposing them.

`output_path` remains outside `EngineConfig`.

Internal diagnostics use Python's standard logging infrastructure.

The reusable extraction components must not force a global logging configuration upon their consumers.

The CLI remains responsible for its own presentation.

---

## D-07 — Transitional compatibility

**Decision: A — APPROVED**

Preserve the existing `search_businesses(query, limit)` boundary temporarily through a compatibility wrapper.

The wrapper must:

- Preserve accepted legacy inputs where feasible.
- Preserve semantic behavior.
- Delegate to the stabilized implementation.
- Avoid maintaining an independent duplicate pipeline.
- Remain identifiable as transitional.

The wrapper is not automatically guaranteed indefinite public support.

Its final removal/deprecation policy must be reviewed before the stable `v1.0.0` contract is finalized.

---

## D-08 — Live Google Maps E2E

**Decision: A — APPROVED**

The live Google Maps E2E remains opt-in.

It is required as a separately evaluated validation activity for significant external-behavior changes, particularly:

- `v0.7.1`
- `v0.7.3`
- `v0.7.5`
- `v0.7.7`

It may also be required in other patches if they affect browser navigation, source execution, or externally observable behavior.

A single external failure is not automatically a deterministic regression.

However, failures must not be ignored without investigating whether they are due to:

- External variability.
- Network conditions.
- DOM changes.
- Browser behavior.
- Implementation regressions.

---

# 8. v0.7.1 — Google Maps Stability

**Status:** APPROVED SCOPE / NOT STARTED

## 8.1 Objective

Stabilize the current Google Maps extraction pipeline without introducing new higher-level architectural boundaries prematurely.

## 8.2 IN SCOPE

- Improve feed readiness handling.
- Review virtual/infinite scrolling behavior.
- Establish bounded termination conditions.
- Reduce unjustified fixed waits.
- Improve detail-panel state synchronization.
- Preserve identity-based enrichment.
- Preserve valid partial Business information.
- Clarify synchronization ownership.
- Strengthen controlled regression coverage.
- Characterize stability and performance under different requested limits.

## 8.3 OUT OF SCOPE

- Formal pagination.
- General retry framework.
- Global browser runtime refactor.
- New Engine facade.
- Formal normalization.
- Deduplication.
- New data sources.
- New error schema.

## 8.4 Components

Primary:

```text
src/scraper/google_maps/result_list.py
src/scraper/google_maps/detail_panel.py
src/engines/selector/lazycharge.py
```

Secondary, when justified:

```text
src/scraper/google_maps/parser.py
src/engines/navigation/
src/engines/selector/
```

## 8.5 Protected contracts

- `limit` controls Businesses processed/returned.
- DOM node counts are not contractually bounded by `limit`.
- Returned Business order is preserved.
- Identity validation prevents known cross-association.
- Recoverable enrichment failures preserve valid prospect data.
- The transitional `search_businesses` entrypoint remains available.

## 8.6 Required evidence

Tests must address, where controllable:

- Feed readiness.
- Empty or missing results.
- Progressive loading.
- Stalled loading.
- Requested limit reached.
- Bounded termination.
- Identity mismatch.
- Partial enrichment.
- Source variability.

Performance measurements must characterize relevant operating limits without treating individual external executions as guaranteed behavior.

## 8.7 Acceptance criteria

- No known uncontrolled scrolling loop.
- Meaningful termination conditions.
- No newly introduced identity contamination.
- Preserved partial-result behavior.
- Deterministic regression suite green.
- Controlled tests for key failure states.
- Live Maps E2E separately evaluated.
- Measurements sufficient to propose an Engine maximum, or explicit documentation of remaining uncertainty.

## 8.8 Exit gate

The patch must provide the evidence needed to evaluate an initial Engine maximum for `v0.7.2`.

It does not select that maximum automatically.

---

# 9. v0.7.2 — EngineConfig Boundary

**Status:** APPROVED SCOPE / NOT STARTED

## 9.1 Objective

Define and introduce the minimal reusable configuration boundary required by the stabilization architecture.

## 9.2 IN SCOPE

- Introduce typed `EngineConfig`.
- Validate configuration values.
- Define requested-limit semantics.
- Define default-limit semantics.
- Apply the Engine maximum policy.
- Introduce the `headless` option.
- Introduce the `website_enrichment` option.
- Propagate configuration to the current pipeline.
- Preserve transitional compatibility.

## 9.3 OUT OF SCOPE

- Configuration profiles.
- Persistent user preferences.
- YAML/JSON configuration systems.
- Batch configuration.
- API membership rules.
- Output path ownership.
- Public configuration of all low-level timing values.

## 9.4 Proposed contract characteristics

- Explicit.
- Typed.
- Predictable defaults.
- Validated.
- Safe against unintended mutation during execution.
- Independent from interactive CLI presentation.
- Reusable by a future Python consumer.

The exact type layout, module path, construction signature, and validation mechanism belong to the patch-level technical design.

## 9.5 Limit policy

```text
requested_limit
default_limit
engine_max_limit
```

must remain conceptually distinct.

The maximum must be approved from evidence.

Values exceeding it must fail explicitly rather than being silently changed.

## 9.6 Acceptance criteria

- Correct default behavior.
- Explicit overrides work.
- Invalid types/values are rejected.
- Requests over maximum are rejected.
- Website enrichment can be disabled without preventing Maps extraction.
- `headless` is propagated to the browser runtime boundary as implementation becomes available.
- Legacy programmatic behavior is preserved as approved.
- Regression suite green.

## 9.7 Mandatory exit gate

**The patch cannot be marked complete until `engine_max_limit` has an approved value or an explicitly approved equivalent operating policy that makes the maximum determinable.**

If measurement evidence is inadequate, stop and request a human decision.

---

# 10. v0.7.3 — Browser Runtime & Lifecycle

**Status:** APPROVED SCOPE / NOT STARTED

## 10.1 Objective

Establish explicit ownership of Playwright/browser resources.

## 10.2 IN SCOPE

- Dedicated internal runtime boundary.
- Browser acquisition.
- Browser/context/page resource ownership.
- Safe release.
- Exceptional cleanup.
- Consumption of `headless`.
- Integration with Navigation Engine.
- Integration with the website inspection workflow.
- Controlled lifecycle testing.

## 10.3 OUT OF SCOPE

- Browser pools.
- Cross-query reuse.
- Concurrency.
- Remote browser farms.
- Parallel scraping.
- Persistent execution jobs.
- General-purpose multi-source execution scheduling.

## 10.4 Ownership rules

The runtime owns resources it acquires.

A source-specific pipeline must not silently take ownership of externally supplied resources.

A consumer may create short-lived child resources only under explicitly defined ownership and cleanup rules.

Successful execution and exceptional execution must both release owned resources.

## 10.5 Acceptance criteria

- Successful cleanup verified.
- Fatal-failure cleanup verified.
- Partial-failure cleanup verified.
- No unintended double close.
- No accidental reuse after closure.
- `headless` behavior verified.
- Controlled tests pass.
- Live Maps E2E evaluated.
- Regression suite green.

---

# 11. v0.7.4 — Logging Boundary

**Status:** APPROVED SCOPE / NOT STARTED

## 11.1 Objective

Separate internal execution diagnostics from the interactive CLI interface.

## 11.2 IN SCOPE

- Standard Python logging.
- Defined logger ownership.
- Replacement of technical `print` statements.
- Appropriate logging levels.
- Relevant operational context.
- Controlled logging tests.
- Preservation of interactive CLI presentation.

## 11.3 OUT OF SCOPE

- Centralized telemetry services.
- Remote log aggregation.
- Distributed tracing.
- SaaS observability.
- Persistent audit database.
- Public logging profile system.

## 11.4 Rules

The extraction pipeline must not depend on interactive output.

Logging must not modify extraction results.

Logging must not replace issues/errors.

Reusable components must not configure global logging policy unexpectedly.

## 11.5 Acceptance criteria

- Internal diagnostics separated from CLI output.
- No reliance on old diagnostic strings as public contracts.
- Consistent logger use.
- Proper levels.
- No uncontrolled global configuration.
- CLI interaction preserved.
- Deterministic tests green.

---

# 12. v0.7.5 — Error Model & Partial Results

**Status:** APPROVED SCOPE / TECHNICAL SCHEMA PENDING

## 12.1 Objective

Introduce structured, predictable error behavior while preserving valid partial extraction results.

## 12.2 IN SCOPE

- Recoverable/fatal distinction.
- Typed fatal exceptions.
- Structured issues.
- Integration with `SearchResult`.
- Source-stage context.
- Controlled failure testing.
- Replacement of silent error recovery where relevant.
- Preservation of valid extracted data.

## 12.3 OUT OF SCOPE

- Distributed recovery.
- General retry framework.
- Persistent incident history.
- Batch error aggregation.
- Membership/API errors.
- Unrelated Business schema expansion.

## 12.4 Approved semantic contract

Recoverable failures:

```text
Preserve valid Business data.
Record a structured issue.
Continue where safely possible.
```

Fatal failures:

```text
Stop the affected search execution.
Release owned runtime resources.
Raise a typed exception.
```

## 12.5 Proposed representation

```python
SearchResult(
    query=query,
    businesses=businesses,
    execution_time=elapsed,
    issues=[],
)
```

The exact issue schema must be approved before implementation.

Candidate metadata includes:

```text
stage
code
severity
message
optional context
optional Business reference
```

These are candidates, not frozen field names.

## 12.6 Compatibility

- Existing Business order preserved.
- `total_found` counts Businesses only.
- ExportService remains outside extraction core.
- Existing CSV/XLSX output remains compatible.
- Error evidence must be available programmatically.
- Logs must not be required to inspect a partial outcome.

## 12.7 Acceptance criteria

- Recoverable detail failure preserves prospect data and records an issue.
- Recoverable website failure preserves Maps data and records an issue.
- Fatal navigation/search failure raises the appropriate typed exception.
- Runtime cleanup remains guaranteed.
- Structured context is testable.
- No silent data loss in covered failure paths.
- Deterministic suite green.
- Live E2E evaluated.

## 12.8 Mandatory design gate

Before implementation:

1. Approve the issue representation.
2. Approve exception categories.
3. Define where an issue is collected and propagated.
4. Define minimum contextual information.
5. Decide representation of unexpected errors without hiding them.

---

# 13. v0.7.6 — ProspectorEngine Facade

**Status:** APPROVED SCOPE / NOT STARTED

## 13.1 Objective

Introduce the reusable internal entrypoint for extraction.

## 13.2 Approved conceptual contract

```python
ProspectorEngine(config).search(query) -> SearchResult
```

## 13.3 IN SCOPE

- Internal facade.
- Configuration consumption.
- Source dispatch for the implemented Google Maps strategy.
- Runtime integration.
- Error model integration.
- Reusable extraction orchestration.
- Controlled Engine tests.
- Independence from interactive CLI code.

## 13.4 OUT OF SCOPE

- Physical Engine package extraction.
- FastAPI/HTTP endpoints.
- Plugin architecture.
- Multiple implemented prospect sources.
- Batch execution.
- Deduplication.
- Normalization.
- Export integration inside the Engine.
- Subscription policies.

## 13.5 Ownership

`ProspectorEngine` is responsible for reusable extraction orchestration.

Source-specific pipelines remain responsible for their own extraction strategies.

The runtime owns browser resources.

`SearchResult` represents extraction outcomes.

`ExportService` remains separately reusable application/export infrastructure.

## 13.6 Acceptance criteria

- Configurable Engine construction.
- Successful Google Maps search through the facade.
- Valid `SearchResult` return.
- Approved partial/fatal semantics.
- No `input()` calls inside the Engine.
- No CLI presentation dependency.
- No dependency on `ExportService`.
- Unsupported source handled through the approved error contract.
- Regression suite green.
- Controlled Engine integration tests pass.

---

# 14. v0.7.7 — CLI Migration & Architectural Closure

**Status:** APPROVED SCOPE / NOT STARTED

## 14.1 Objective

Migrate the interactive CLI to `ProspectorEngine` and formally complete the stabilization line.

## 14.2 IN SCOPE

- CLI adapter migration.
- Limit input with default.
- Configuration construction.
- Engine invocation.
- Result presentation.
- Existing export choices.
- Transitional wrapper compatibility.
- Error presentation.
- Integration/regression verification.
- Documentation alignment.
- Architectural closure audit.

## 14.3 OUT OF SCOPE

- Full CLI redesign.
- Configuration profiles.
- Batch commands.
- Multi-input.
- Deduplication.
- Normalization.
- API endpoints.
- Jobs.
- Physical Engine separation.

## 14.4 CLI responsibility

The CLI:

- Collects interactive input.
- Applies presentation-level defaults.
- Validates or reports invalid inputs.
- Constructs Engine configuration.
- Invokes `ProspectorEngine`.
- Presents results.
- Invokes `ExportService` when requested.
- Presents errors in a user-appropriate way.

The CLI must not directly orchestrate Google Maps-specific scraping stages.

## 14.5 Transitional entrypoint

`search_businesses()` must remain available through the approved compatibility strategy.

It must not independently duplicate the stabilized pipeline.

## 14.6 Acceptance criteria

- Interactive search works through `ProspectorEngine`.
- `main.py` no longer directly orchestrates `search_businesses`.
- Default and explicit requested limits work.
- Invalid limits are handled predictably.
- Output order and Business values preserved.
- CSV/XLSX compatibility preserved.
- Structured partial issues handled appropriately.
- Fatal errors are communicated without breaking cleanup.
- Full deterministic regression suite green.
- Live Google Maps E2E evaluated.
- Official documentation reflects CURRENT behavior.
- Global `v0.7.x` closure checklist completed.

---

# 15. Cross-patch testing strategy

Every patch must have:

1. Relevant unit tests.
2. Controlled integration tests when applicable.
3. Existing deterministic regression suite.
4. A separate E2E evaluation when externally relevant.
5. Documented test results.
6. A review of what behavior is protected versus deliberately unfrozen.

## 15.1 Test matrix

| Patch | Unit | Controlled integration | Live Maps E2E |
|---|---|---|---|
| `v0.7.1` | Required | Required | Required |
| `v0.7.2` | Required | Required | Conditional |
| `v0.7.3` | Required | Required | Required |
| `v0.7.4` | Required | As applicable | Conditional |
| `v0.7.5` | Required | Required | Required |
| `v0.7.6` | Required | Required | When needed |
| `v0.7.7` | Required | Required | Required |

The live E2E remains opt-in and independently evaluated.

## 15.2 Deterministic validation

At minimum:

```powershell
python -m compileall -q src
python -m pytest -q
git diff --check
git status --short
```

The current audit virtual environment can be used while available.

## 15.3 Contracts that must remain protected

- SearchQuery preservation.
- Ordered Business results.
- `total_found` semantics.
- Partial-result preservation.
- ExportService CSV/XLSX schema.
- Website Engine's existing validated behavior.
- Selector infrastructure behavior.
- Reusable module boundaries.

## 15.4 Behavior that must not be frozen

- Exact DOM node counts.
- Google Maps business names.
- Exact selectors.
- Current fixed waits.
- Current diagnostic `print` messages.
- Wall-clock timings.
- Current accidental exception classes.
- Mojibake and unrelated parser defects.
- Incomplete contact/about/content type metadata.

---

# 16. Deferred decisions and decision gates

The Master Plan is approved with controlled deferred technical decisions.

| Item | Required resolution | Deadline |
|---|---|---|
| `engine_max_limit` | Evidence-based value and policy | Before v0.7.2 closure |
| Config API details | Exact type/signature/default representation | Before v0.7.2 implementation |
| Runtime API | Acquisition and ownership contract | Before v0.7.3 implementation |
| Logging implementation | Logger ownership/levels/handlers | Before v0.7.4 implementation |
| Issue schema | Exact fields and semantics | Before v0.7.5 implementation |
| Exception hierarchy | Fatal/configuration/source error types | Before v0.7.5 implementation |
| Facade integration | Module placement and dispatch boundary | Before v0.7.6 implementation |
| Wrapper policy | Compatibility details and migration mechanics | Before v0.7.7 implementation |

The following remain outside the mandatory `v0.7.x` decisions unless evidence reveals a direct dependency:

- Official full Python support matrix, to be resolved before `v1.0.0`.
- Contact/about/content type completion.
- Extended Business identity/output model.
- Multi-email output semantics.
- v0.9 batch/merge decisions.
- Concurrency.
- Physical Engine packaging.

No deferred decision may be silently resolved by Codex when its implications affect public contracts, architecture ownership, or approved version boundaries.

---

# 17. Risks

## R-01 — Overgeneralization

Prematurely converting Google Maps-specific behavior into universal infrastructure.

**Mitigation:** share only clearly reusable responsibilities.

## R-02 — External source variability

Google Maps may change UI/DOM/navigation behavior.

**Mitigation:** controlled semantic tests plus separately evaluated live smoke checks.

## R-03 — Configuration complexity

Exposing internal technical values creates unnecessary API surface.

**Mitigation:** minimal EngineConfig and internal defaults.

## R-04 — Resource leaks

Ownership confusion may leave browser resources running after exceptions.

**Mitigation:** dedicated runtime and explicit cleanup contracts.

## R-05 — Silent partial failures

Existing broad catches may hide failures.

**Mitigation:** structured error model with recoverable evidence.

## R-06 — Contract instability

Changes to `SearchResult` or Engine may affect future consumers.

**Mitigation:** design before implementation and preserve backward-compatible defaults where reasonable.

## R-07 — Scope expansion

Architectural refactoring could introduce v0.8/v0.9 or post-v1 functionality.

**Mitigation:** explicit IN/OUT scope for every patch.

## R-08 — False stability

Passing one Google Maps run could be interpreted as source reliability.

**Mitigation:** require deterministic invariants and explicit evaluation of external variability.

---

# 18. Change management

## 18.1 Per-patch implementation protocol

Each patch must follow:

```text
Technical planning
       |
       v
Human architecture review
       |
       v
Patch plan approval
       |
       v
Codex implementation
       |
       v
Tests and validation
       |
       v
Review of actual diff
       |
       v
Documentation update
       |
       v
Patch acceptance
       |
       v
Git checkpoint
```

A patch must not begin implementation until its technical scope and unresolved decisions have been approved.

## 18.2 Codex instructions

Codex implementation prompts must include:

- Baseline commit.
- Approved patch scope.
- Relevant source paths.
- Required contracts.
- Prohibited changes.
- Tests to add.
- Acceptance criteria.
- Explicit stop conditions.
- Validation commands.
- Required final report.

Codex must not introduce architectural decisions outside the approved patch plan.

## 18.3 Scope deviations

If a previously unknown dependency blocks implementation, Codex must report:

- Exact blocker.
- Relevant source evidence.
- Alternatives.
- Impact.
- Recommendation.

It must not expand patch scope automatically.

## 18.4 Versioning and commits

Each accepted patch should have a clear checkpoint.

Tags/releases are created only after their corresponding validation and human acceptance.

The baseline remains available for comparison.

No patch should bundle unrelated features or cleanup solely for convenience.

---

# 19. Documentation policy

The official documentation must continue distinguishing:

- CURRENT.
- TECHNICAL_DEBT.
- TARGET.
- HISTORICAL.
- DEFERRED_DESIGN.
- POST_V1.

`docs/roadmap.md` remains the public normative version-boundary reference.

`docs/architecture.md` remains the public architectural reference.

The approved Master Plan provides detailed internal implementation authority for `v0.7.x`.

After an implementation patch is accepted, official documentation should be updated to reflect the resulting CURRENT behavior.

The project philosophy and historical design rationale must remain preserved.

Do not convert the README into a running audit log.

---

# 20. Global v0.7.x closure checklist

The line is complete only if all conditions below hold.

## Extraction

- [ ] Google Maps loading behavior stabilized within defined observable limits.
- [ ] Identity-based enrichment preserved.
- [ ] Valid partial Business data preserved.
- [ ] Requested limits behave consistently.
- [ ] No known uncontrolled loops.

## Configuration

- [ ] Minimal EngineConfig implemented.
- [ ] Requested/default/maximum limits distinguished.
- [ ] Maximum policy approved and enforced.
- [ ] Invalid requests rejected explicitly.
- [ ] Headless configuration supported.
- [ ] Website enrichment can be configured.

## Runtime

- [ ] Browser lifecycle ownership explicit.
- [ ] Cleanup guaranteed on success and failure.
- [ ] No ambiguous resource ownership.
- [ ] No unintended persistent pooling or cross-query state.

## Diagnostics and errors

- [ ] Logging separated from CLI presentation.
- [ ] Recoverable issues structured.
- [ ] Fatal exceptions typed.
- [ ] Partial data preserved.
- [ ] Logging not used as the error contract.

## Engine

- [ ] ProspectorEngine exists.
- [ ] Engine consumes configuration.
- [ ] Engine returns SearchResult.
- [ ] Engine is independent from CLI presentation.
- [ ] Engine does not own export.
- [ ] Unsupported sources have defined failure behavior.

## CLI

- [ ] CLI consumes ProspectorEngine.
- [ ] Interactive limit supported.
- [ ] Existing extraction experience preserved.
- [ ] Existing export workflow preserved.
- [ ] Transitional compatibility addressed.

## Quality

- [ ] Deterministic regression suite green.
- [ ] Required controlled integration tests green.
- [ ] Live Maps E2E evaluated.
- [ ] Technical debt appropriately classified.
- [ ] Official documentation accurate.
- [ ] No v0.8 normalization work introduced.
- [ ] No v0.9 multi-input/dedup introduced.
- [ ] No architecture blockers deferred to v0.8.

---

# 21. Exit criterion

The formal exit criterion of `v0.7.x` is:

> Prospector CLI provides a stable internal extraction boundary through `ProspectorEngine(config).search(query)`, with explicit runtime ownership, minimal configuration, defined error semantics, preserved regression contracts, and a CLI adapter consuming the Engine. All remaining work required to implement deterministic normalization can proceed in `v0.8.x` without first resolving architectural debt assigned to `v0.7.x`.

This does not require:

- Zero technical debt.
- Perfectly deterministic external Google Maps behavior.
- Multiple implemented sources.
- A standalone Engine package.
- API functionality.
- Batch execution.
- Distributed execution.

It requires the absence of unresolved architecture blockers that would prevent the approved `v0.8.x` scope.

---

# 22. Final approval record

**Approved decisions:**

| ID | Approved option |
|---|---|
| D-01 | A |
| D-02 | A |
| D-03 | A |
| D-04 | A |
| D-05 | A |
| D-06 | A |
| D-07 | A |
| D-08 | A |

**Approved release count:** 7

**Approved release sequence:**

```text
v0.7.1 — Google Maps Stability
v0.7.2 — EngineConfig
v0.7.3 — Browser Runtime
v0.7.4 — Logging
v0.7.5 — Error Model
v0.7.6 — ProspectorEngine
v0.7.7 — CLI Migration & Closure
```

**Approved version boundaries:**

```text
v0.8.x — Normalization
v0.9.x — Multi-input + Deduplication
v1.0.0 — First stable extraction-ready release
Post-v1 — Possible physical Engine extraction
```

**Deferred:** numerical Engine maximum, exact technical APIs, issue schema, exception hierarchy, and other explicitly listed patch-level designs.

**Master Plan status:** APPROVED

**Patch technical planning:** PENDING

**Production implementation:** NOT STARTED

---

# 23. Next phase — Patch Implementation Planning

The next activity is to produce the detailed implementation plan for each patch, beginning with:

`v0.7.1 — Google Maps Stability`

Each patch-level plan must refine the Master Plan into:

1. Exact source inventory.
2. Defects and debt addressed.
3. Invariants to preserve.
4. Detailed implementation strategy.
5. Expected file changes.
6. Test cases.
7. Acceptance criteria.
8. Risks and rollback conditions.
9. Documentation changes.
10. Codex execution instructions.
11. Human approval gate.
12. Definition of Done.

The patch plan must not contradict this Master Plan.

Any required scope change must be proposed as a documented amendment and approved before implementation.

**End of approved v0.7.x Implementation Master Plan — v1.0.**
# Prospector CLI v1.0.0 — Release Candidate Report

Date: 2026-10-08. Branch: `v1.0.0`. Source HEAD and local implementation commit: `0499f9f` (`feat(v1.0.0): finalize CLI hardening and Edge portable candidate`). No push, tag, GitHub Release, or A3 publication.

## Status and gates

**RELEASE CANDIDATE READY / R20 OWNER_ACCEPTANCE_PENDING.** P101–P108 PASS. R01–R07, R09–R14 and R16–R19 PASS (17 PASS gates); R08 **OWNER_WAIVED / DEFERRED_POST_RELEASE**, never PASS; R15 OPTIONAL_SKIPPED; R20 owner-only pending. No active implementation or release blocker is known. This is not a stable release declaration.

## Runtime and policy

Version `1.0.0` in source, packaged menu, and portable documentation. Windows portable requires installed Microsoft Edge Stable; tested version `154.0.4258.62`. Playwright 1.61.0 uses the supported `msedge` channel. **Visible is default; Background is available.** No browser executable or Playwright browser-cache payload is redistributed. The portable includes Python/runtime dependencies and does not require a Python or Playwright-browser installation on the owner's machine.

## Source and packaged validation

Final source state: `compileall -q src` PASS; project-`venv` offline suites 229 unit PASS, 69 integration PASS, 298 total PASS, one live E2E deselected; `git diff --check` and staged check PASS. No source code changed after that regression; subsequent edits were documentary. Final Git worktree is clean after the local commit.

R09 PASS: scoped Windows process-group isolation keeps CLI Ctrl+C away from the Playwright driver. Packaged No continued through subsequent real detail operations. Packaged Yes reached a safe checkpoint, completed BrowserRuntime cleanup and returned `CANCELLED` to the menu in 12.97 seconds in the final R09 development build, with no pending-task warning, traceback, partial export, checkpoint/resume artifact, or attributable orphan. See `R09CancellationEvidence.md`.

R10 PASS only under the approved **best-effort** console-close contract. An offline real-process atexit test terminated its Edge/driver normally; the packaged forced `WM_CLOSE` simulation did not close within 20 seconds and is recorded as inconclusive, not as a successful forced-X test. See `R10ConsoleCloseEvidence.md`.

R19 PASS under the owner's amended definition: source regression plus current-host packaged smoke. The same-source development onedir completed Visible single search, repeated execution, a Background two-query batch, source/global progress, metrics and summaries, Next/Previous pagination, CSV and independent XLSX files with seven approved columns, logs directory, and normal exit. See `R19PackagedSmokeEvidence.md`. This was **not** clean-machine validation.

The exact final ZIP was extracted to a temporary `temp/RC relocated test 20261008/` path with spaces and launched with `PLAYWRIGHT_BROWSERS_PATH` pointing to a nonexistent location. Its v1.0.0 main menu and Visible default displayed correctly. An extra live one-result search in that PTY produced no conclusive result during the bounded observation; the test session was interrupted, so no final-ZIP search PASS is inferred from that attempt. The temporary extraction contained no export and was removed after inspection; the ZIP remains intact. The complete R19 functional smoke remains the prior same-source package evidence; this limitation is disclosed for the owner test.

## Exact owner-testable artifact

- ZIP: `Prospector-CLI-v1.0.0-win64.zip` (accepted local artifact; not tracked in Git)
- Size: **53,658,917 bytes**.
- SHA-256: `A219F5A2F9A060A16135B4A61DC3CDC940659111EEE1790933E30B7C50245C1C`.
- Inventory: 276 ZIP entries; `Prospector-CLI-v1.0.0-win64/prospector.exe`, `_internal/`, `exports/`, `logs/`, `README_PORTABLE.md`, `LICENSE`, `PYTHON_LICENSE.txt`, `THIRD_PARTY_NOTICES.md`, and `THIRD_PARTY_LICENSES/` present. Zero browser executable/cache entries. The clean final package has no test exports.

If any ZIP content changes, this checksum is invalid and the artifact must be rebuilt and rehashed.

## Accepted residual risk and next step

R08 clean/isolated external-Windows validation was **not executed**. The owner waived it for this initial release and deferred it to post-release compatibility checks; machine-specific Windows, Edge, or enterprise-policy issues may still be discovered. The installed Edge Stable prerequisite and R10 forced-close limitation remain explicit. No matching/deduplication policy or public Engine business contract changed. The owner should complete the two tracks in `OwnerAcceptanceChecklist.md`, then decide R20. A3 requires separate authorization.

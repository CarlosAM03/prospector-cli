# v1.0.0 validation matrix

Tracked closure update: the owner accepted R20 after the local release candidate report; see [OWNER_ACCEPTANCE.md](OWNER_ACCEPTANCE.md). Earlier evidence rows retain their original measurements.

| Gate | Patch | Status | Evidence |
|---|---|---|---|
| R01 | P103 | PASS | Rich adapter, semantic unit tests, 276 full offline PASS; later packaged/live UX remains separate R08/R19 |
| R02 | P102 | PASS | Private neutral callback; no Rich below presentation; observer equality/failure tests; 268 full offline PASS |
| R03 | P102 | PASS | `MetricsInventory.md` exact/derived/conditional definitions; distinct observed/extracted; no fabricated number |
| R04 | P105/P106 | PASS — EDGE FALLBACK | `BrowserModeEvidence.md`: Edge Stable 154.0.4258.62, two completed headed/background pairs match counts/identity/cleanup; two Background navigation failures in bounded sample justify approved Visible-default fallback, Background selectable |
| R05 | P106 | PASS — LOCAL DEVELOPMENT BUILD | PyInstaller 6.22.3 `onedir`, Python 3.13.4, Playwright 1.61.0; v1.0.0 menu opens; 273-file latest build, no browser executable |
| R06 | P106 | PASS — BROWSER RUNTIME AVAILABILITY | Installed Edge Stable through `channel="msedge"`; relocated package completed bounded Visible and Background live searches with `PLAYWRIGHT_BROWSERS_PATH` deliberately nonexistent; mock unavailable/launch-failure path controlled; no browser bundled |
| R07 | P106 | PASS — LOCAL RELOCATION | Copied/renamed onedir outside repository to a spaced non-admin `%TEMP%` path; menu, Edge Visible/Background, CSV/XLSX and logs worked there. Does not substitute for R08 clean OS |
| R08 | P107 | OWNER_WAIVED / DEFERRED_POST_RELEASE | Owner exception 2026-10-08; `CleanMachineEvidence.md`. No clean-machine test executed and no PASS claimed. Relocation on the primary host is R07/R19 support only |
| R09 | P104/P107 | PASS | `R09CancellationEvidence.md`: scoped Windows driver process group, No continues through multiple real detail operations; Yes final package returns `CANCELLED` to menu in 12.97 s, exit 0, no pending tasks/traceback/export/orphan process; 298 full offline PASS |
| R10 | P104/P107 | PASS — BEST EFFORT | `R10ConsoleCloseEvidence.md`: real-process atexit driver PID 27884 exited, unit close-once/fatal tests and packaged R09 cleanup pass. Test-owned WM_CLOSE did not close within 20 s and is expressly inconclusive; forced console closure is not guaranteed |
| R11 | P104 | PASS | Rotating local logs, 1 MB × 3 bounded files, tests; 285 full offline PASS |
| R12 | P104 | PASS | Portable export root, CSV/XLSX, unique/headers-only/path/write-failure tests; 285 full offline PASS |
| R13 | P101 | PASS | `DependencyInventory.md`; import scan, pip metadata, no removals; 263 full offline PASS |
| R14 | P106 | PASS — NO BROWSER REDISTRIBUTION | Owner Edge amendment; latest onedir has zero browser executables/cache payload; external Edge not shipped. Python, Playwright/Node, Rich, openpyxl, PyInstaller and transitive notices/licenses inspected in `PackagingEvidence.md` |
| R15 | P106 | SKIPPED NON-BLOCKING | Official SignPath eligibility and release-process requirements not low-friction/established for this candidate; no signing request |
| R16 | P106/P108 | PASS — MEASURED | Edge development onedir 133,471,535 bytes and cold menu 1.172 s; final RC ZIP 53,658,917 bytes, 276 entries, SHA-256 in `ReleaseCandidateReport.md`; no arbitrary size threshold or clean-host performance claim |
| R17 | P101/P108 | PASS | `src/version.py`, semantic unit test, final onedir/ZIP version 1.0.0 and relocated menu v1.0.0; `ReleaseCandidateReport.md` |
| R18 | P101/P108 | PASS | `ContractInventory.md` final P108 audit: public model/normalization/P92 identity files unchanged; Engine signatures/result semantics preserved; approved CLI/runtime/packaging changes only |
| R19 | P107 | PASS — AMENDED CURRENT HOST | `R19PackagedSmokeEvidence.md`: compileall, 229 unit / 69 integration / 298 full offline PASS (1 E2E deselected); packaged Visible single, Background two-query batch, CSV/XLSX seven columns, repeated search, metrics, real Next/Previous pagination, normal exit; R09/R10 separately PASS. No external-machine claim |
| R20 | Owner | OWNER ACCEPTED | Explicit owner decision for the v1.0.0 portable RC; [tracked acceptance](OWNER_ACCEPTANCE.md). Tag/release publication remains pending the independent freeze audit |

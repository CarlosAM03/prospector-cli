# R19 — source regression and packaged smoke on primary Windows host

Status: **PASS under the 2026-10-08 owner amendment**. This is not clean-machine testing: R08 remains **OWNER_WAIVED / DEFERRED_POST_RELEASE**.

Source state: project `venv`, live E2E disabled, external `%TEMP%` basetemp. `compileall -q src` PASS; 229 unit PASS; 69 integration PASS; 298 full offline PASS with one live E2E deselected; `git diff --check` and cached diff check PASS. The accepted prior baseline was 226/69/295.

Packaged current-host state: Edge-based `onedir` development build `temp/b-20261008-094047/Prospector-CLI-v1.0.0-win64/`, same R09 source state. It opened v1.0.0 menu, showed Visible as default and Background as option, completed a Visible one-result single search, displayed summary/metrics/result view, exported a CSV, accepted another search in the same session, completed a two-query Background batch, displayed per-query and batch summaries/metrics, exported two independent XLSX files and exited normally (code 0; no traceback). The batch showed 2 observed / 2 exportable / 0 suppressed / 2 unverified, consistent with exact verified-identity deduplication. `exports/` held exactly the three test-owned files and `logs/` was present. CSV had one data row and the approved seven columns; each XLSX `Businesses` sheet had header plus one row and the same seven columns: Name, Category, Address, Phone, Email, Website, Language. No test-owned packaged process remained after normal exit.

An additional one-query Visible packaged search with limit 11 reached the result viewer's second page. The UI offered Next, accepted it, offered Previous, accepted it, returned to the first page and exited normally (code 0). This closes the earlier development-build pagination evidence gap without claiming full catalog completeness.

R09 packaged Ctrl+C No/Yes evidence is in `R09CancellationEvidence.md`; R10 best-effort evidence and forced-console limitation are in `R10ConsoleCloseEvidence.md`. Previous owner manual live batch evidence supports the broader UI, but is not relabeled as clean-machine validation. Microsoft Edge Stable 154.0.4258.62 was the tested installed browser. Initial v1.0.0 portability on a separate Windows installation remains an accepted residual risk, not a R19 PASS claim.

The transient executable smoke harness was removed from the planning folder after this summary. The test-owned development build and its live export files remain local evidence, not release payload.

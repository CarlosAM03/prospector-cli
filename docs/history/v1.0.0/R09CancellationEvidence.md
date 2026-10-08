# R09 — Windows Ctrl+C and BrowserRuntime cleanup (2026-10-08)

Status: **PASS**, packaged Edge-based development portable; A3 and R20 remain withheld.

## Cause and bounded correction

The CLI and Playwright Node driver initially shared the Windows console process group. A generated Ctrl+C reached both; an offline `about:blank` call failed with `TargetClosedError`, and `BrowserRuntime` reported failed cleanup despite a declined cancellation. A scoped startup-only override now starts **only Playwright's `run-driver` process** in a new Windows process group. BrowserRuntime continues to own the browser, pages, Playwright context and cleanup. There are no workers, queues, parallel searches or detached persistent service. The temporary spawn override is restored immediately after synchronous Playwright startup, including error paths.

Confirmed cancellation remains a flag in the signal handler. The CLI checks it only at stage boundaries, completed candidate progress or a feed scroll checkpoint; it does not raise inside the handler. A bounded source failure after confirmation is reported as cancellation only after BrowserRuntime has unwound without a cleanup-failure marker. A cleanup failure remains fatal, not `CANCELLED`.

Timeout audit of production operations relevant to R09: Edge launch explicitly 30 seconds; navigation has a 50-second stage deadline with 10–15-second per-call caps; feed has a 90-second total deadline, 80 attempts maximum, 1.5-second scroll observation and 0.1–10-second waits; detail selection has an 8-second per-candidate deadline; website navigation has an explicit 15-second timeout; Playwright's installed 1.61.x default for otherwise unparameterized operations is finite 30 seconds. Feed checkpoint after each completed scroll prevents waiting for the entire feed when cancellation is pending. No global process-kill timer was introduced.

## Observed tests

- Offline driver diagnostic, before correction: `about:blank` `page.wait_for_timeout(10000)` plus declined Ctrl+C produced `TargetClosedError` and cleanup warning. After correction: the same operation printed `READY`, `CONTINUED`, driver exit code 0. Two further Runtime enter/launch/exit cycles and one deliberate fatal-exception unwind each returned driver exit code 0. No accumulated driver process was observed.
- Focused offline final: 62 PASS across CLI, BrowserRuntime, result-list and controlled source tests. Complete source regression: compileall PASS, 229 unit PASS, 69 integration PASS, 298 full offline PASS, one live E2E deselected, `git diff --check` PASS.
- Packaged No path: development build `temp/b-20261008-093701/` received Ctrl+C at 4.22 s; answer No. A Playwright API trace 12 seconds later showed continuing Maps detail clicks, navigation and field reads for multiple candidates, with no signal-caused navigation error. A subsequent Yes cancelled at the next safe boundary, returned to the main menu and exited 0. This distinguishes continued operation from merely returning to a prompt.
- Packaged Yes path on that build: Ctrl+C at 5.08 s; controlled `Execution cancelled safely` at 21.47 s from start; main menu, exit code 0.
- Final R09 development build `temp/b-20261008-094047/`, including the 30-second launch bound and feed checkpoint: confirmed Yes at 5.38 s, safe cancellation and main-menu return at 12.97 s, exit code 0. No traceback or Playwright pending-task warning in captured output; `logs/prospector.log` length 0. No file under its `exports/`. Post-exit process inspection found no `prospector`/Node/Edge process attributable to this build. The preceding No/Yes packaged probe likewise left no attributable process/export.

No checkpoint or resume artifact is implemented or created by cancellation. The cancelled execution's unexported state is discarded. The earliest packaged probe with a shared process group and a separate probe-harness encoding failure remain historical failed diagnostics, not gate evidence. The diagnostic Python harnesses were removed from the planning folder after this summary; the durable regression is in `tests/unit/`.

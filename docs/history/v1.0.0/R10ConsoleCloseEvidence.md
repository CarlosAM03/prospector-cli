# R10 — best-effort console-close cleanup (2026-10-08)

Status: **PASS for the documented best-effort contract, with forced-console limitation**. This is not a guarantee that Windows grants time for full cleanup when a console window is forcibly closed.

`BrowserRuntime` owns Playwright/browser/page cleanup and registers an idempotent interpreter-exit callback. Deterministic unit tests verify ordinary cleanup, fatal-error cleanup, close-once behavior and the atexit callback. The separate offline real-process probe opened Edge `about:blank`, deliberately omitted explicit `__exit__`, then exited normally: process exit code 0 and test-owned Playwright driver PID 27884 absent afterward, with no attributable children. Packaged R09 Yes tests also unwound through BrowserRuntime and left no attributable driver/browser process.

A one-off packaged active-search console-window close simulation targeted only test-owned PID 2948 (`WM_CLOSE` to its returned console HWND 1772188). The target did **not** exit within the 20-second observation, so this experiment is **inconclusive as a Windows console-X simulation**, not a claimed successful forced-close cleanup. The harness then terminated only its exact test-owned process; post-test inspection found no process attributable to the package. No owner Edge session was touched. A Windows forced close may bypass or abbreviate Python atexit; the product deliberately promises best effort, not confirmation or guaranteed cleanup for this OS event. Ctrl+C with verified cleanup is separately proven by R09 and is the recommended controlled cancellation path.

The transient executable console-close and atexit probes were removed from the planning folder after this record.

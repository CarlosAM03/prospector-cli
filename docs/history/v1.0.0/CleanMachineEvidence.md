# v1.0.0 Clean-Machine Evidence — owner exception

Status: **OWNER_WAIVED / DEFERRED_POST_RELEASE** (R08). This is not PASS.

Executed on a separate clean/isolated Windows machine: **NO**. No second clean Windows machine is currently available; Windows Sandbox is unavailable on the present host. The portable has been relocated and run without Playwright-managed browser-cache dependency on the primary development host, with installed Microsoft Edge Stable as an external prerequisite, but this does not satisfy the original R08 test.

Owner decision (2026-10-08): non-blocking for the initial v1.0.0 release. The owner prioritizes the first CLI release and subsequent Engine/API workstream and knowingly accepts possible machine-specific Windows, Edge or enterprise-policy defects. When another Windows host is available, validate after release and treat discoveries as post-release maintenance/hardening (normally v1.0.1/v1.0.2 unless later policy changes). Do not perform that work in this release-candidate cycle.

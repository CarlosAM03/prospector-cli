# Prospector CLI v1.0.0 — Known limitations and prerequisites

These are accepted scope or environmental limits, not a claim of a release defect.

- The first packaged target is Windows 10/11 x64. Microsoft Edge Stable must be installed; the ZIP does not bundle a browser or install Edge. Enterprise Edge policy, required extensions, proxies and other managed-device controls may affect automation.
- Visible is the default. Background is supported but showed lower reliability than Visible in bounded pre-release validation.
- Google Maps and inspected websites can change or fail. Recoverable issues may yield valid **partial** results; neither a requested limit nor a completed query guarantees catalog completeness.
- Cross-query deduplication suppresses only observations with verified identity in the approved namespace. An `UNVERIFIED` observation remains exportable and may look commercially duplicated; no name, address, phone, email, website, domain or similarity matching is used.
- No persistence, checkpoint/resume, auto-update, API, SaaS or background job system is included. Confirmed Ctrl+C discards unexported execution state after verified cleanup; forced console closure offers only best-effort cleanup.
- A separate clean/isolated Windows-machine validation was not performed. The owner waived R08 for this initial release and deferred external-host compatibility testing until after publication. Machine-specific Windows/Edge issues may therefore require later patch maintenance.

The owner accepted this scope at R20. The repository freeze audit passed, and Prospector CLI v1.0.0 is published as a stable GitHub Release.

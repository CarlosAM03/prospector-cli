# P105 / R04 — bounded headed/background evidence (2026-10-07)

Authorization: owner A2 activation for v1.0.0. Environment: Windows 11 x64, Python 3.13.4, Playwright 1.61.0, local Chromium 149.0.7827.55. Each run used the accepted `ProspectorEngine.search_many()` path with **one query** (to retain identity sidecar), website enrichment enabled, no export, and limit 1 or 2. This is targeted mode evidence, not general live acceptance or a source-catalog completeness claim.

| Query / limit | Mode | Outcome | Maps observed | Extracted / normalized | Verified / unverified | Issues | Navigation / feed / detail / website / query seconds | Cleanup |
|---|---|---|---:|---:|---:|---:|---|---|
| Starbucks Zona Rio / Tijuana / 1 | Visible | SUCCESS | 1 | 1 / 1 | 1 / 0 | 0 | 6.572 / 0.264 / 3.202 / 1.038 / 13.200 | yes |
| same / 1 | Background, first attempt | FAILED before completed navigation | unavailable | 0 / 0 | 0 / 0 | unavailable | stage timings unavailable; batch 20.823 | not established by metric |
| same / 1 | Background, controlled retry | SUCCESS | 1 | 1 / 1 | 1 / 0 | 0 | 4.470 / 0.073 / 1.360 / 0.843 / 7.521 | yes |
| Starbucks / Tijuana / 2 | Visible | SUCCESS | 2 | 2 / 2 | 2 / 0 | 0 | 5.054 / 0.361 / 3.485 / 2.043 / 12.629 | yes |
| same / 2 | Background | SUCCESS | 2 | 2 / 2 | 2 / 0 | 0 | 4.993 / 0.136 / 2.945 / 1.036 / 9.974 | yes |

For successful paired runs, navigation/feed/detail/P92 verified identity/website/normalization/result counts and cleanup were operationally equivalent for the sampled candidates. One background attempt failed before a completed navigation measurement; a same-input retry and the second paired case succeeded. This is not evidence of systematic semantic data divergence, but it is a reliability observation to retain. Stage timings are observed samples, not performance guarantees.

**R04 decision:** Background/headless remains the default, Visible/headed remains selectable. This follows ADR-010's preferred branch on the observed paired outcomes; the evidence does not assert universal headless reliability. Any future systematic semantic divergence would require a new investigation, not silent policy change.

## Edge-specific R04 repetition — 2026-10-08

Owner A2 authorizes bounded live evidence. Windows 11 x64, project `venv` Python 3.11.9, Playwright 1.61.0, **installed Microsoft Edge Stable 154.0.4258.62** through `channel="msedge"`. One-query `ProspectorEngine.search_many()` runs preserved the P92 identity sidecar. Website enrichment was enabled; no export. An initial Visible limit-1 run completed, but its post-run evidence reader used a nonexistent `verified_count` property and exited before printing counts; it was repeated rather than treating that reader error as a product failure.

| Query / limit | Edge mode | Outcome | Observed / extracted / normalized | Verified / unverified | Issues | Navigation / feed / detail / website / query seconds | Cleanup |
|---|---|---|---|---|---:|---|---|
| Starbucks Zona Rio / Tijuana / 1 | Visible | SUCCESS | 1 / 1 / 1 | 1 / 0 | 0 | 5.607 / 0.174 / 2.901 / 1.065 / 11.885 | yes |
| same / 1 | Background, first batch attempt | FAILED, navigation category before completion | 0 / unavailable / unavailable | unavailable | unavailable | navigation stage timing unavailable; batch 18.667 | not established by metric |
| same / 1 | Background, controlled retry | FAILED, navigation category before completion | 0 / unavailable / unavailable | unavailable | unavailable | navigation stage timing unavailable; batch 17.853 | not established by metric |
| same / 1 | Background, direct single diagnostic | SUCCESS | 1 / 1 / 1 | sidecar not measured | 0 | not instrumented; full run about 11.3 | normal owned runtime exit |
| same / 1 | Background, final sidecar measurement | SUCCESS | 1 / 1 / 1 | 1 / 0 | 0 | 4.561 / 0.111 / 1.409 / 1.171 / 8.778 | yes |
| Starbucks / Tijuana / 2 | Visible | SUCCESS | 2 / 2 / 2 | 2 / 0 | 0 | 8.197 / 0.420 / 4.024 / 1.673 / 15.978 | yes |
| same / 2 | Background | SUCCESS | 2 / 2 / 2 | 2 / 0 | 0 | 5.119 / 0.325 / 2.947 / 2.058 / 12.192 | yes |

For the two completed sidecar pairs, Edge Visible and Background matched extraction/normalization cardinality, verified identities, zero issues, and cleanup. This supports **functional equivalence when execution completes**. However two consecutive Background limit-1 attempts failed at navigation, versus no such Visible failures in this bounded sample. The cause of those two navigation failures is not established; the later success rules out a persistent inability to use Edge headless. This is a materially weaker observed reliability profile for Background, not proof of a systematic semantic difference or universal failure rate. Under ADR-010's previously approved R04 fallback, **Visible becomes the v1.0.0 default, Background remains selectable** pending further packaged evidence. No navigation implementation or business rule was changed to hide the failures.

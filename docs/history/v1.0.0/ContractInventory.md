# P101 contract inventory — initial R18

| Contract | Classification | Accepted invariant |
|---|---|---|
| `ProspectorEngine.search`, `search_many` | PUBLIC_STABLE | Signatures, one-query and ordered sequential batch semantics unchanged |
| `EngineConfig`, `SearchQuery` | PUBLIC_STABLE | Engine limit 1–100/default 50; source enum; headless/enrichment flags |
| `SearchResult`, `Business`, `NormalizedBusiness`, `SearchIssue` | PUBLIC_STABLE | Independent aligned views, issues, extracted total; 12 business fields |
| `BatchQuery`, `BatchQueryResult`, `BatchSearchResult` | PUBLIC_STABLE | Engine 1–5, safe failures, order, provenance, verified-only cross-query suppression |
| Typed `ProspectorError` subclasses | PUBLIC_STABLE | Fatal category/chaining; recoverable issues separate |
| `ExportService` | PUBLIC_STABLE | Seven CSV/XLSX columns; separate batch files; no Engine export |
| `metrics_sink` | INTERNAL | Existing Google Maps measurement dict; reconcile in P102 |
| CLI single/batch flows | RELEASE_UI_CONTRACT | v1 menu, 2–3 interactive batch, confirmation, summary, 10-row pagination, browser choice |
| Source selectors, P92 URL parsing | IMPLEMENTATION_DETAIL | Preserve accepted extraction/identity semantics; no heuristic matching |

Final R18 audit is due in P108; this inventory is not a declaration that v1 UX exists yet.

## P108 final contract freeze — 2026-10-08

R18 **PASS**. Final `git diff HEAD` inspection found no change to public model files, normalization implementation, Google Maps detail identity, or P92 source-identity code. Engine/global-pipeline changes are neutral progress/metric events; public search signatures, original/normalized result assembly, sequential batch semantics, verified-only deduplication, and seven-column export contract remain intact. BrowserRuntime hardening, CLI presentation, Edge-only external runtime policy, and portable packaging are within the approved v1.0.0 scope. The 229-unit/69-integration/298-total offline regression and current-host packaged smoke support this audit. R20 is reserved for owner acceptance; this is not a release declaration.

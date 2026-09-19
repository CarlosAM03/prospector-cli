# Research Scripts

This directory contains exploratory/manual tooling used to investigate browser behavior, Google Maps DOM behavior, extraction strategies and architectural assumptions.

These scripts are not permanent pytest contracts and may become obsolete after their findings are incorporated into implementation or documentation. Research notes must distinguish observed facts from hypotheses and must not be used to claim a production mechanism unless source code confirms it.

Research tooling is not part of the default regression suite and must not introduce a public dependency on Google Maps for ordinary tests.

### Historical Google Maps DOM findings — HISTORICAL

Earlier research investigated SPA detail-panel reuse, URL changes, synchronization by state and Playwright interaction methods. Those findings informed later Navigation Engine, LazyCharge and detail-panel work. They explain architectural evolution, but a historical observation such as a single JavaScript extraction pass must not be treated as the current implementation contract unless `src/` confirms it.

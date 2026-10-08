# Unit Tests

This directory contains isolated, deterministic tests for current intentional contracts.

Unit tests must avoid external network dependency and real browser execution. Current scope includes models/default semantics, normalization rules/engine, exact batch selection, CLI semantics and cancellation, mocked BrowserRuntime/Windows driver isolation, metrics, version, utilities, Website components, selector behavior and explicitly named characterization of Google Maps summary-parser encoding.

Mandatory normalization and verified-only interquery deduplication are current unit-test contracts. Speculative semantic validation or heuristic matching is not. Exact waits, selectors, timestamps and mojibake must not be frozen as desired behavior.

The R09 cancellation and driver-process tests are durable deterministic expectations here. One-off live console probes are not prerequisites for this suite.

# Unit Tests

This directory contains isolated, deterministic tests for current intentional contracts.

Unit tests must avoid external network dependency and real browser execution. Current scope includes models/default semantics, utilities, Website parser/metadata/language/email components, selector registry/fallback behavior and explicitly named characterization of current Google Maps summary-parser encoding behavior.

Formal normalization, validation, deduplication and other future components are not current unit-test contracts. Exact waits, selectors, timestamps and mojibake must not be frozen as desired behavior.

Typical unit-test subjects include parsers, deterministic data transformations and small scoring/helper functions. A future normalizer may belong here after `v0.8.x` defines its contract; its presence in historical test examples does not mean a production normalizer exists today.

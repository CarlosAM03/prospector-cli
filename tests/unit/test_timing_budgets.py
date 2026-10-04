"""Finite remaining budgets for controllable Playwright operations."""

import pytest
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from engines import _timing


def test_remaining_timeout_is_bounded_by_local_cap_and_global_deadline(monkeypatch):
    monkeypatch.setattr(_timing.time, "monotonic", lambda: 10.0)
    assert _timing.remaining_ms(10.25, 1000) == 250
    assert _timing.remaining_ms(11.0, 100) == 100
    with pytest.raises(PlaywrightTimeoutError, match="budget exhausted"):
        _timing.remaining_ms(10.0, 1000)

"""Internal finite-budget helper for controllable Playwright operations."""

import time

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError


def remaining_ms(deadline: float, cap_ms: int) -> int:
    """Bound an operation by both its local cap and the remaining deadline."""
    remaining = int((deadline - time.monotonic()) * 1000)
    if remaining <= 0:
        raise PlaywrightTimeoutError("operation budget exhausted")
    return max(1, min(cap_ms, remaining))

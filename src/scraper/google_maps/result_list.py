"""Ordered, bounded collection from the Google Maps virtual result feed."""

import time
import logging

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from engines._timing import remaining_ms
from engines.selector.lazycharge import LazyChargeEngine
from models.business import Business

from .parser import parse_business_summary
from .selectors import create_selector_engine


# Internal safety budgets, not public configuration or source-total claims.
MAX_SCROLL_ATTEMPTS = 80
MAX_IDLE_ATTEMPTS = 6
MAX_LOADING_SECONDS = 90
SCROLL_OBSERVATION_SECONDS = 1.5
logger = logging.getLogger(__name__)


def extract_businesses(page, limit: int, issue_collector=None) -> list[dict]:
    """Collect valid first-seen source candidates in discovery order.

    Source hrefs prevent a recycled card from being processed twice. They
    are not a business deduplication or a name-merging rule.
    """
    deadline = time.monotonic() + MAX_LOADING_SECONDS
    selector = create_selector_engine(page)
    feed = LazyChargeEngine(page, "google_maps").wait_feed(
        timeout=remaining_ms(deadline, 10000)
    )

    if limit <= 0:
        # Preserve the legacy path: navigation, feed and result election still
        # occur, but no Businesses are processed or returned.
        selector.locator("results")
        return []

    links = feed.locator(selector.selectors("results")[0])
    results: list[dict] = []
    seen_hrefs: set[str] = set()
    idle = 0
    attempts = 0

    while attempts < MAX_SCROLL_ATTEMPTS and time.monotonic() < deadline:
        new_valid = 0
        timed_out = False
        # Capture each visible batch before scrolling can recycle its nodes.
        for index in range(links.count()):
            try:
                link = links.nth(index)
                name = link.get_attribute(
                    "aria-label", timeout=remaining_ms(deadline, 1000)
                )
                href = link.get_attribute(
                    "href", timeout=remaining_ms(deadline, 1000)
                )
                if not name or not href or href in seen_hrefs:
                    continue

                article = link.locator(selector.selectors("result_article")[0])
                blocks = article.locator(selector.selectors("info_block")[0])
                category, address, phone = parse_business_summary(
                    blocks, deadline=deadline
                )
            except PlaywrightTimeoutError:
                timed_out = True
                break
            seen_hrefs.add(href)
            new_valid += 1
            results.append({
                "href": href,
                "identity": {"index": index, "name": name, "href": href},
                "business": Business(
                    name=name, category=category, address=address, phone=phone
                ),
            })
            if len(results) >= limit:
                logger.debug("Maps feed reached requested limit: count=%d", len(results))
                return results

        if timed_out:
            break
        idle = 0 if new_valid else idle + 1
        if idle >= MAX_IDLE_ATTEMPTS:
            break
        try:
            _charge_results(page, feed, links, seen_hrefs, deadline)
        except PlaywrightTimeoutError:
            break
        attempts += 1

    if not results:
        # Without an evidence-backed Maps empty marker, zero cards are not
        # proof that the source returned a legitimate empty result.
        logger.warning("Maps feed indeterminate: attempts=%d idle=%d", attempts, idle)
        raise LookupError("Google Maps feed ended without verifiable results")
    logger.info(
        "Maps feed returned available candidates: count=%d attempts=%d idle=%d",
        len(results), attempts, idle,
    )
    if issue_collector is not None and len(results) < limit:
        issue_collector.record("feed", "partial_results")
    return results


def _charge_results(page, feed, links, seen_hrefs, deadline) -> None:
    """Scroll the source feed and wait only for useful candidate progress."""
    feed.hover(timeout=remaining_ms(deadline, 1000))
    remaining_ms(deadline, 1000)
    page.mouse.wheel(0, 1800)
    observation_end = min(deadline, time.monotonic() + SCROLL_OBSERVATION_SECONDS)
    while time.monotonic() < observation_end:
        for index in range(links.count()):
            link = links.nth(index)
            href = link.get_attribute(
                "href", timeout=remaining_ms(deadline, 1000)
            )
            name = link.get_attribute(
                "aria-label", timeout=remaining_ms(deadline, 1000)
            )
            if href and name and href not in seen_hrefs:
                return
        try:
            page.wait_for_timeout(remaining_ms(observation_end, 100))
        except PlaywrightTimeoutError:
            return

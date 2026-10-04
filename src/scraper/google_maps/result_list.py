"""Ordered, bounded collection from the Google Maps virtual result feed."""

import time
import logging

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


def extract_businesses(page, limit: int) -> list[dict]:
    """Collect valid first-seen source candidates in discovery order.

    Source hrefs prevent a recycled card from being processed twice. They
    are not a business deduplication or a name-merging rule.
    """
    selector = create_selector_engine(page)
    feed = LazyChargeEngine(page, "google_maps").wait_feed()

    if limit <= 0:
        # Preserve the legacy path: navigation, feed and result election still
        # occur, but no Businesses are processed or returned.
        selector.locator("results")
        return []

    links = feed.locator(selector.selectors("results")[0])
    results: list[dict] = []
    seen_hrefs: set[str] = set()
    deadline = time.monotonic() + MAX_LOADING_SECONDS
    idle = 0
    attempts = 0

    while attempts < MAX_SCROLL_ATTEMPTS and time.monotonic() < deadline:
        new_valid = 0
        # Capture each visible batch before scrolling can recycle its nodes.
        for index in range(links.count()):
            link = links.nth(index)
            name = link.get_attribute("aria-label")
            href = link.get_attribute("href")
            if not name or not href or href in seen_hrefs:
                continue

            article = link.locator(selector.selectors("result_article")[0])
            blocks = article.locator(selector.selectors("info_block")[0])
            category, address, phone = parse_business_summary(blocks)
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

        idle = 0 if new_valid else idle + 1
        if idle >= MAX_IDLE_ATTEMPTS:
            break
        _charge_results(page, feed, links, seen_hrefs, deadline)
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
    return results


def _charge_results(page, feed, links, seen_hrefs, deadline) -> None:
    """Scroll the source feed and wait only for useful candidate progress."""
    feed.hover()
    page.mouse.wheel(0, 1800)
    observation_end = min(deadline, time.monotonic() + SCROLL_OBSERVATION_SECONDS)
    while time.monotonic() < observation_end:
        for index in range(links.count()):
            link = links.nth(index)
            href = link.get_attribute("href")
            name = link.get_attribute("aria-label")
            if href and name and href not in seen_hrefs:
                return
        page.wait_for_timeout(
            min(100, max(1, int((observation_end - time.monotonic()) * 1000)))
        )

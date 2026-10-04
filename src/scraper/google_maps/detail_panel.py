"""Identity-gated enrichment from a Google Maps detail panel."""

import re
import time
from urllib.parse import unquote

from engines.selector.lazycharge import LazyChargeEngine
from models.business import Business

from .parser import parse_business_summary  # historical import compatibility
from .selectors import create_selector_engine


def extract_place_id(href: str) -> str | None:
    match = re.search(r"1s([^!/?#]+)", unquote(href))
    return match.group(1) if match else None


def read_text(panel, selector):
    try:
        return panel.locator(selector).last.inner_text(timeout=1000).strip()
    except Exception:
        return None


def read_href(panel, selector):
    try:
        return panel.locator(selector).last.get_attribute("href", timeout=1000)
    except Exception:
        return None


def _equivalent_name(left: str, right: str) -> bool:
    """Only trim, collapse whitespace and ignore letter case (H02)."""
    return " ".join(left.split()).casefold() == " ".join(right.split()).casefold()


def _panel_text(panel) -> str | None:
    try:
        return panel.inner_text(timeout=1000).strip()
    except Exception:
        return None


def _target_link(page, href):
    links = page.locator("a[href*='/maps/place/']")
    for index in range(links.count()):
        link = links.nth(index)
        if link.get_attribute("href") == href:
            return link
    return None


def _fields(panel, selector):
    return {
        "address": read_text(panel, selector.selectors("address")[0]),
        "phone": read_text(panel, selector.selectors("phone")[0]),
        "website": read_href(panel, selector.selectors("website")[0]),
    }


def enrich_business(
    page, href, business: Business, identity: dict | None = None,
    issue_collector=None,
) -> Business:
    """Keep the summary unless target URL and fresh panel agree on identity."""
    expected_id = extract_place_id(href)
    expected_name = (identity or {}).get("name", business.name)
    if not expected_id or not expected_name:
        _record_skip(issue_collector, href, "identity_unverifiable")
        return business

    selector = create_selector_engine(page)
    panel_selector = selector.selectors("detail_panel")[0]
    name_selector = selector.selectors("business_name")[0]
    previous_panel = page.locator(panel_selector).last
    previous_text = _panel_text(previous_panel)
    previous_url = page.url

    try:
        target = _target_link(page, href)
        if target is None:
            _record_skip(issue_collector, href, "target_unavailable")
            return business
        target.click(timeout=3000)
    except Exception as error:
        _record_skip(issue_collector, href, "click_unavailable", error)
        return business

    deadline = time.monotonic() + 8
    while time.monotonic() < deadline:
        try:
            panel = LazyChargeEngine(page, "google_maps").wait_detail_panel(
                timeout=500
            )
            if extract_place_id(page.url) != expected_id:
                page.wait_for_timeout(100)
                continue
            title = read_text(panel, name_selector)
            current_text = _panel_text(panel)
            if not title or not _equivalent_name(title, expected_name):
                page.wait_for_timeout(100)
                continue
            # An already visible panel, especially one with the same name,
            # cannot certify that the click selected a different Business.
            if previous_text and current_text == previous_text:
                page.wait_for_timeout(100)
                continue
            first = _fields(panel, selector)
            page.wait_for_timeout(100)
            second = _fields(panel, selector)
            if first != second:
                continue
            if (
                extract_place_id(page.url) != expected_id
                or not _equivalent_name(read_text(panel, name_selector) or "", expected_name)
                or (previous_url != page.url and _panel_text(panel) == previous_text)
            ):
                continue
            for field, value in second.items():
                if value:
                    setattr(business, field, value)
            return business
        except Exception as error:
            # A panel transition/optional read failure is recoverable for this
            # prospect; never merge data from an unverified panel.
            _record_skip(issue_collector, href, "panel_unavailable", error)
            return business
    _record_skip(issue_collector, href, "identity_unverifiable")
    return business


def _record_skip(issue_collector, href, reason, error=None):
    if issue_collector is not None:
        issue_collector.record(
            "detail", reason, candidate=href, error=error,
        )

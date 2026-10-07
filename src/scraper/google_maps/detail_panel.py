"""Identity-gated enrichment from a Google Maps detail panel."""

import re
import time
from urllib.parse import unquote

from engines._timing import remaining_ms
from engines.selector.lazycharge import LazyChargeEngine
from models.business import Business

from .parser import parse_business_summary  # historical import compatibility
from .selectors import create_selector_engine


def extract_place_id(href: str) -> str | None:
    matches = re.findall(r"(?:^|!)1s([^!/?#]+)", unquote(href))
    return matches[0] if matches else None


def _url_has_place_id(url: str, expected_id: str) -> bool:
    # A Maps URL can carry multiple data segments after a route transition.
    # Require an entire 1s token, never a substring of another place ID.
    return expected_id in re.findall(r"(?:^|!)1s([^!/?#]+)", unquote(url))


def read_text(panel, selector, deadline=None):
    try:
        locator = panel.locator(selector).last
        if hasattr(locator, "count") and locator.count() == 0:
            return None
        timeout = remaining_ms(deadline, 200) if deadline is not None else 200
        return locator.inner_text(timeout=timeout).strip()
    except Exception:
        return None


def read_href(panel, selector, deadline=None):
    try:
        locator = panel.locator(selector).last
        if hasattr(locator, "count") and locator.count() == 0:
            return None
        timeout = remaining_ms(deadline, 200) if deadline is not None else 200
        return locator.get_attribute("href", timeout=timeout)
    except Exception:
        return None


def _equivalent_name(left: str, right: str) -> bool:
    """Only trim, collapse whitespace and ignore letter case (H02)."""
    return " ".join(left.split()).casefold() == " ".join(right.split()).casefold()


def _panel_text(panel, deadline=None) -> str | None:
    try:
        timeout = remaining_ms(deadline, 1000) if deadline is not None else 1000
        return panel.inner_text(timeout=timeout).strip()
    except Exception:
        return None


_NODE_ID = """element => {
    const key = '__prospector_detail_nodes';
    const state = window[key] || (window[key] = {next: 0, ids: new WeakMap()});
    if (!state.ids.has(element)) state.ids.set(element, ++state.next);
    return state.ids.get(element);
}"""


def _node_id(locator, deadline):
    try:
        if hasattr(locator, "count") and locator.count() == 0:
            return None
        return locator.evaluate(_NODE_ID, timeout=remaining_ms(deadline, 150))
    except Exception:
        return None


def _matching_panel(
    page, panel_selector, name_selector, expected_name, previous_text, deadline
):
    panels = page.locator(panel_selector)
    unchanged = None
    for index in range(panels.count()):
        panel = panels.nth(index)
        if panel.is_visible() and _equivalent_name(
            read_text(panel, name_selector, deadline) or "", expected_name
        ):
            if _panel_text(panel, deadline) != previous_text:
                return panel
            unchanged = panel
    return unchanged


def _target_link(page, href, deadline):
    links = page.locator("a[href*='/maps/place/']")
    for index in range(links.count()):
        link = links.nth(index)
        if link.get_attribute(
            "href", timeout=remaining_ms(deadline, 1000)
        ) == href:
            return link
    return None


def _recover_target_link(page, href, deadline):
    """Revisit a recycled Maps card; only the exact source href is clickable."""
    try:
        feed = LazyChargeEngine(page, "google_maps").wait_feed(
            timeout=remaining_ms(deadline, 500)
        )
        # Small reverse pass, then forward pass after a prior candidate was
        # selected. Exhaustion always leaves the summary unchanged.
        for distance in (-1800,) * 4 + (1800,) * 8:
            feed.hover(timeout=remaining_ms(deadline, 500))
            remaining_ms(deadline, 500)
            page.mouse.wheel(0, distance)
            page.wait_for_timeout(remaining_ms(deadline, 100))
            target = _target_link(page, href, deadline)
            if target is not None:
                return target
    except Exception:
        return None
    return None


def _fields(panel, selector, deadline):
    return {
        "address": read_text(panel, selector.selectors("address")[0], deadline),
        "phone": read_text(panel, selector.selectors("phone")[0], deadline),
        "website": read_href(panel, selector.selectors("website")[0], deadline),
    }


def enrich_business(
    page, href, business: Business, identity: dict | None = None,
    issue_collector=None, identity_sink: dict | None = None,
) -> Business:
    """Keep the summary unless target URL and fresh panel agree on identity."""
    expected_id = extract_place_id(href)
    expected_name = (identity or {}).get("name", business.name)
    if not expected_id or not expected_name:
        _record_skip(issue_collector, href, "identity_unverifiable")
        return business

    selector = create_selector_engine(page)
    deadline = time.monotonic() + 8
    panel_selector = selector.selectors("detail_panel")[0]
    name_selector = selector.selectors("business_name")[0]
    previous_panel = page.locator(panel_selector).last
    previous_text = _panel_text(previous_panel, deadline)
    previous_url = page.url
    previous_fields = _fields(previous_panel, selector, deadline) if previous_text else {}
    previous_nodes = {
        field: _node_id(previous_panel.locator(selector.selectors(field)[0]).last, deadline)
        for field in ("address", "phone", "website")
    } if previous_text else {}

    try:
        target = _target_link(page, href, deadline)
        if target is None:
            target = _recover_target_link(page, href, deadline)
            if target is None:
                _record_skip(issue_collector, href, "target_unavailable")
                return business
        target.click(timeout=remaining_ms(deadline, 3000))
    except Exception as error:
        _record_skip(issue_collector, href, "click_unavailable", error)
        return business

    while time.monotonic() < deadline:
        try:
            LazyChargeEngine(page, "google_maps").wait_detail_panel(
                timeout=remaining_ms(deadline, 500)
            )
            if not _url_has_place_id(page.url, expected_id):
                page.wait_for_timeout(remaining_ms(deadline, 100))
                continue
            panel = _matching_panel(
                page, panel_selector, name_selector, expected_name,
                previous_text, deadline,
            )
            if panel is None:
                page.wait_for_timeout(remaining_ms(deadline, 100))
                continue
            title = read_text(panel, name_selector, deadline)
            current_text = _panel_text(panel, deadline)
            if not title or not _equivalent_name(title, expected_name):
                page.wait_for_timeout(remaining_ms(deadline, 100))
                continue
            # An already visible panel, especially one with the same name,
            # cannot certify that the click selected a different Business.
            if previous_text and current_text == previous_text:
                page.wait_for_timeout(remaining_ms(deadline, 100))
                continue
            first = _fields(panel, selector, deadline)
            page.wait_for_timeout(remaining_ms(deadline, 100))
            second = _fields(panel, selector, deadline)
            if first != second:
                continue
            if (
                not _url_has_place_id(page.url, expected_id)
                or not _equivalent_name(
                    read_text(panel, name_selector, deadline) or "", expected_name
                )
                or (
                    previous_url != page.url
                    and _panel_text(panel, deadline) == previous_text
                )
            ):
                continue
            uncertain_fields = False
            for field, value in second.items():
                if not value:
                    continue
                node = _node_id(
                    panel.locator(selector.selectors(field)[0]).last, deadline
                )
                # A shared value can be legitimate when its field element was
                # replaced for the verified target. A retained element with
                # unchanged content is still ambiguous after a panel switch.
                if (value == previous_fields.get(field)
                        and (node is None or node == previous_nodes.get(field))):
                    uncertain_fields = True
                    continue
                setattr(business, field, value)
            if uncertain_fields:
                _record_skip(issue_collector, href, "fields_unverifiable")
            if identity_sink is not None:
                identity_sink["verified_selected_url"] = page.url
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
            "detail", reason, candidate=extract_place_id(href), error=error,
        )

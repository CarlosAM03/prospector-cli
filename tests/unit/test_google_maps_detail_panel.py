"""Controlled identity transitions for Google Maps detail enrichment."""

import pytest

from models.business import Business
from scraper.google_maps import detail_panel


def href(key, name="Cafe"):
    return f"/maps/place/{name}/data=!1s{key}!"


class Field:
    def __init__(self, page, selector):
        self.page = page
        self.selector = selector

    @property
    def last(self):
        return self

    def count(self):
        if self.selector == "h1":
            return int(self.page.state.get("title") is not None)
        if "address" in self.selector:
            return int(self.page.state.get("address") is not None)
        if "phone" in self.selector:
            return int(self.page.state.get("phone") is not None)
        return int(self.page.state.get("website") is not None)

    def inner_text(self, timeout=1000):
        if self.selector == "h1":
            value = self.page.state["title"]
        elif "address" in self.selector:
            value = self.page.state.get("address")
        elif "phone" in self.selector:
            value = self.page.state.get("phone")
        else:
            value = None
        if value is None:
            raise LookupError(self.selector)
        return value

    def get_attribute(self, name, timeout=1000):
        return self.page.state.get("website")

    def wait_for(self, **kwargs):
        return None

    def evaluate(self, expression, timeout=None):
        return self.page.state.get("node_ids", {}).get(self.selector)


class Panel:
    def __init__(self, page):
        self.page = page

    def inner_text(self, timeout=1000):
        return self.page.state["text"]

    def is_visible(self):
        return bool(self.page.state.get("visible", True))

    def locator(self, selector):
        return Field(self.page, selector)


class PanelList:
    def __init__(self, page):
        self.page = page

    @property
    def last(self):
        return Panel(self.page)

    @property
    def first(self):
        return self

    def nth(self, index):
        return Panel(self.page)

    def count(self):
        return int(self.page.state.get("visible", True))

    def is_visible(self):
        return bool(self.page.state.get("visible", True))


class Target:
    def __init__(self, page):
        self.page = page

    def get_attribute(self, name, timeout=None):
        return self.page.target_href

    def click(self, timeout=3000):
        self.page.clicked = True
        if self.page.state.get("click_fails"):
            raise RuntimeError("click failed")
        self.page.after_click(self.page)


class TargetList:
    def __init__(self, page):
        self.page = page

    def count(self):
        return int(self.page.target_present)

    def nth(self, index):
        return Target(self.page)


class Page:
    def __init__(self, target_href, after_click=None):
        self.target_href = target_href
        self.target_present = True
        self.clicked = False
        self.clock = 0.0
        self.url = "https://www.google.com/maps/place/Old/data=!1sold!"
        self.state = {"title": "Old", "text": "Old panel", "address": "Old address"}
        self.after_click = after_click or valid_transition
        self.on_wait = lambda page: None

    def locator(self, selector):
        if selector.startswith("a["):
            return TargetList(self)
        return PanelList(self)

    def wait_for_timeout(self, ms):
        self.clock += ms / 1000
        self.on_wait(self)


def valid_transition(page):
    page.url = f"https://www.google.com{page.target_href}"
    page.state = {
        "title": "Cafe", "text": "Cafe new panel", "address": "New address",
        "phone": "555 123 4567", "website": "https://example.test",
    }


def run(monkeypatch, page, name="Cafe", business=None):
    monkeypatch.setattr(detail_panel.time, "monotonic", lambda: page.clock)
    business = business or Business(name=name, address="Summary address")
    returned = detail_panel.enrich_business(
        page, page.target_href, business, {"name": name, "href": page.target_href}
    )
    assert returned is business
    return business


def test_t_d01_valid_identity_merges_verified_fields(monkeypatch):
    page = Page(href("target"))
    business = run(monkeypatch, page)
    assert page.clicked
    assert (business.address, business.phone, business.website) == (
        "New address", "555 123 4567", "https://example.test"
    )


def test_t_d02_missing_link_or_stale_panel_keeps_summary(monkeypatch):
    page = Page(href("target"))
    page.target_present = False
    assert run(monkeypatch, page).address == "Summary address"
    page = Page(href("target"), after_click=lambda p: setattr(p, "url", f"https://www.google.com{p.target_href}"))
    assert run(monkeypatch, page).address == "Summary address"


def test_t_d03_place_id_mismatch_and_substring_collision(monkeypatch):
    page = Page(href("target"), after_click=lambda p: setattr(p, "url", "https://x/maps/place/X/data=!1starget-extra!"))
    assert run(monkeypatch, page).address == "Summary address"


def test_t_d04_same_name_cannot_override_wrong_place_id(monkeypatch):
    def wrong(page):
        page.url = "https://x/maps/place/Cafe/data=!1sother!"
        page.state = {"title": "Cafe", "text": "Other Cafe", "address": "Wrong"}
    assert run(monkeypatch, Page(href("target"), wrong)).address == "Summary address"


def test_t_d05_waits_for_coherent_optional_fields(monkeypatch):
    page = Page(href("target"))
    def update(p):
        if p.clock >= 0.1:
            p.state["phone"] = "555 123 4567"
    page.on_wait = update
    business = run(monkeypatch, page)
    assert business.phone == "555 123 4567"


def test_t_d06_missing_optional_fields_preserve_summary(monkeypatch):
    def partial(page):
        page.url = f"https://x{page.target_href}"
        page.state = {"title": "Cafe", "text": "Cafe partial", "address": None,
                      "phone": None, "website": None}
    business = run(monkeypatch, Page(href("target"), partial))
    assert business.address == "Summary address"
    assert business.phone is None


def test_t_d07_identity_change_between_read_and_commit_discards_fields(monkeypatch):
    page = Page(href("target"))
    page.on_wait = lambda p: setattr(p, "url", "https://x/maps/place/Other/data=!1sother!")
    assert run(monkeypatch, page).address == "Summary address"


def test_t_d08_only_whitespace_and_case_equivalence_is_allowed(monkeypatch):
    page = Page(href("target"))
    business = run(monkeypatch, page, name="  caFE   ")
    assert business.address == "New address"


@pytest.mark.parametrize("name", ["Cafe!", "Café", "Cafe and Co"])
def test_t_d09_punctuation_accent_other_changes_are_rejected(monkeypatch, name):
    assert run(monkeypatch, Page(href("target")), name=name).address == "Summary address"


def test_t_d10_missing_place_id_preserves_summary(monkeypatch):
    page = Page("/maps/place/Cafe/")
    assert run(monkeypatch, page).address == "Summary address"
    assert not page.clicked


def test_stale_optional_fields_are_not_merged_after_new_title_and_url(monkeypatch):
    def transition(page):
        page.url = f"https://www.google.com{page.target_href}"
        page.state = {
            "title": "Cafe", "text": "Cafe new heading, old optional fields",
            "address": "Old address", "phone": "Old phone",
            "website": "https://old.test",
        }

    page = Page(href("target"), transition)
    page.state["phone"] = "Old phone"
    page.state["website"] = "https://old.test"
    business = Business(name="Cafe", address="Summary address", phone="Summary phone")
    result = run(monkeypatch, page, business=business)
    assert (result.address, result.phone, result.website) == (
        "Summary address", "Summary phone", None
    )


def test_shared_optional_values_from_new_field_nodes_are_valid(monkeypatch):
    def transition(page):
        page.url = f"https://www.google.com{page.target_href}"
        page.state = {
            "title": "Cafe", "text": "Cafe detail", "address": "Shared address",
            "phone": "Shared phone", "website": "https://shared.test",
            "node_ids": {"button[data-item-id='address'] .Io6YTe": 4,
                         "a[data-item-id^='phone:'] .Io6YTe": 5,
                         "a[data-item-id='authority']": 6},
        }

    page = Page(href("target"), transition)
    page.state.update({
        "address": "Shared address", "phone": "Shared phone",
        "website": "https://shared.test",
        "node_ids": {"button[data-item-id='address'] .Io6YTe": 1,
                     "a[data-item-id^='phone:'] .Io6YTe": 2,
                     "a[data-item-id='authority']": 3},
    })
    business = run(monkeypatch, page)
    assert (business.address, business.phone, business.website) == (
        "Shared address", "Shared phone", "https://shared.test"
    )


def test_transformed_url_can_contain_other_data_tokens(monkeypatch):
    def transition(page):
        valid_transition(page)
        page.url = "https://www.google.com/maps/place/Cafe/data=!1sother!3m1!1starget!"

    page = Page(href("target"), transition)
    assert run(monkeypatch, page).address == "New address"


def test_matching_panel_ignores_an_old_visible_panel(monkeypatch):
    class VisiblePanel:
        def __init__(self, title):
            self.title = title

        def is_visible(self):
            return True

        def locator(self, selector):
            return self

        @property
        def last(self):
            return self

        def inner_text(self, timeout=None):
            return self.title

    class Panels:
        def count(self):
            return 2

        def nth(self, index):
            return [VisiblePanel("Old"), VisiblePanel("Cafe")][index]

    class MultiPage:
        def locator(self, selector):
            return Panels()

    panel = detail_panel._matching_panel(
        MultiPage(), "div[role='main']", "h1", "Cafe", "Old", None
    )
    assert panel.title == "Cafe"


def test_matching_panel_prefers_fresh_same_name_business(monkeypatch):
    class VisiblePanel:
        def __init__(self, text):
            self.text = text

        def is_visible(self):
            return True

        def locator(self, selector):
            class Title:
                @property
                def last(self):
                    return self

                def inner_text(self, timeout=None):
                    return "Cafe"

            return Title()

        @property
        def last(self):
            return self

        def inner_text(self, timeout=None):
            return self.text

    class Panels:
        def __init__(self):
            self.items = [VisiblePanel("Cafe prior panel"), VisiblePanel("Cafe target panel")]

        def count(self):
            return len(self.items)

        def nth(self, index):
            return self.items[index]

    class MultiPage:
        def locator(self, selector):
            return Panels()

    panel = detail_panel._matching_panel(
        MultiPage(), "div[role='main']", "h1", "Cafe", "Cafe prior panel", None
    )
    assert panel.text == "Cafe target panel"


def test_failed_click_keeps_summary(monkeypatch):
    page = Page(href("target"))
    page.state["click_fails"] = True
    business = run(monkeypatch, page)
    assert business.address == "Summary address"


def test_late_panel_transition_can_still_enrich(monkeypatch):
    page = Page(href("target"), lambda current: None)

    def later(current):
        if current.clock >= 0.3:
            valid_transition(current)
            current.on_wait = lambda later_page: None

    page.on_wait = later
    business = run(monkeypatch, page)
    assert business.address == "New address"


def test_absent_optional_fields_do_not_consume_auto_waits(monkeypatch):
    def transition(page):
        page.url = f"https://www.google.com{page.target_href}"
        page.state = {"title": "Cafe", "text": "Cafe detail", "address": None,
                      "phone": None, "website": None}

    page = Page(href("target"), transition)
    business = run(monkeypatch, page)
    assert business.address == "Summary address"
    assert page.clock <= 0.2


def test_p92_identity_sink_requires_confirmed_target_panel(monkeypatch):
    feature = "0x80d94840107994c1:0x95f9d1c6296e50c3"
    place_id = "ChIJwZR5EEBI2YARw1BuKcbR-ZU"
    candidate = (
        "https://www.google.com/maps/place/Cafe/data="
        f"!4m7!3m6!1s{feature}!8m2!3d32.5!4d-117!19s{place_id}"
    )

    def transition(page):
        page.url = (
            "https://www.google.com/maps/place/Cafe/data="
            f"!3m6!1s{feature}!8m2!3d32.5!4d-117"
        )
        page.state = {"title": "Cafe", "text": "Cafe confirmed",
                      "address": "New address", "phone": None, "website": None}

    monkeypatch.setattr(detail_panel.time, "monotonic", lambda: page.clock)
    page = Page(candidate, transition)
    capture = {}
    detail_panel.enrich_business(
        page, candidate, Business("Cafe"), {"name": "Cafe"},
        identity_sink=capture,
    )
    assert capture["verified_selected_url"] == page.url

    def wrong(page):
        transition(page)
        page.state["title"] = "Other Cafe"

    page = Page(candidate, wrong)
    capture = {}
    detail_panel.enrich_business(
        page, candidate, Business("Cafe"), {"name": "Cafe"},
        identity_sink=capture,
    )
    assert capture == {}

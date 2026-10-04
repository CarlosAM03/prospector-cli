"""Offline end-to-end candidate collection through recycled-card detail clicks."""

from types import SimpleNamespace

from scraper.google_maps import detail_panel, result_list, website_enrichment


def card(name, key):
    return {
        "aria-label": name,
        "href": f"/maps/place/{name}/data=!1s{key}!",
        "address": f"{name} address",
        "website": f"https://{key}.test",
    }


class Field:
    def __init__(self, page, selector):
        self.page, self.selector = page, selector

    @property
    def last(self):
        return self

    def inner_text(self, timeout=None):
        if self.selector == "business_name":
            return self.page.panel["title"]
        return self.page.panel.get(self.selector) or ""

    def get_attribute(self, name, timeout=None):
        return self.page.panel.get("website")


class Panel:
    def __init__(self, page):
        self.page = page

    def inner_text(self, timeout=None):
        return self.page.panel["text"]

    def locator(self, selector):
        return Field(self.page, selector)

    def is_visible(self):
        return True


class Panels:
    def __init__(self, page):
        self.page = page

    @property
    def last(self):
        return Panel(self.page)

    def count(self):
        return 1

    def nth(self, index):
        return Panel(self.page)


class Blocks:
    def count(self):
        return 0


class Article:
    def locator(self, selector):
        return Blocks()


class Link:
    def __init__(self, page, data):
        self.page, self.data = page, data

    def get_attribute(self, name, timeout=None):
        return self.data.get(name)

    def locator(self, selector):
        return Article()

    def click(self, timeout=None):
        assert self.data in self.page.cards
        self.page.clicked.append(self.data["href"])
        self.page.url = "https://www.google.com" + self.data["href"]
        self.page.panel = {
            "title": self.data["aria-label"],
            "text": self.data["aria-label"] + " new panel",
            "address": self.data["address"],
            "phone": None,
            "website": self.data["website"],
        }


class Links:
    def __init__(self, page):
        self.page = page

    def count(self):
        return len(self.page.cards)

    def nth(self, index):
        return Link(self.page, self.page.cards[index])


class Feed:
    def __init__(self, page):
        self.page = page

    def locator(self, selector):
        return Links(self.page)

    def hover(self, timeout=None):
        return None


class Mouse:
    def __init__(self, page):
        self.page = page

    def wheel(self, x, y):
        if y > 0:
            self.page.batch = min(1, self.page.batch + 1)
        elif self.page.recovery_enabled:
            self.page.batch = max(0, self.page.batch - 1)


class Page:
    def __init__(self, recovery_enabled=True):
        self.batches = [[card("A", "id_a")], [card("B", "id_b")]]
        self.batch = 0
        self.recovery_enabled = recovery_enabled
        self.clock = 0.0
        self.mouse = Mouse(self)
        self.clicked = []
        self.url = "https://www.google.com/maps/place/Old/data=!1sold!"
        self.panel = {"title": "Old", "text": "Old panel", "address": "Old address"}

    @property
    def cards(self):
        return self.batches[self.batch]

    def locator(self, selector):
        return Links(self) if selector.startswith("a[") else Panels(self)

    def wait_for_timeout(self, ms):
        self.clock += ms / 1000


class Selector:
    def __init__(self, page):
        self.page = page

    def selectors(self, name):
        return [name]


class Wait:
    def __init__(self, page, profile):
        self.page = page

    def wait_feed(self, timeout=10000):
        return Feed(self.page)

    def wait_detail_panel(self, timeout=10000):
        return Panel(self.page)


def setup(monkeypatch, recovery_enabled=True):
    page = Page(recovery_enabled)
    monkeypatch.setattr(result_list, "create_selector_engine", lambda p: Selector(p))
    monkeypatch.setattr(result_list, "LazyChargeEngine", Wait)
    monkeypatch.setattr(detail_panel, "create_selector_engine", lambda p: Selector(p))
    monkeypatch.setattr(detail_panel, "LazyChargeEngine", Wait)
    monkeypatch.setattr(result_list.time, "monotonic", lambda: page.clock)
    monkeypatch.setattr(detail_panel.time, "monotonic", lambda: page.clock)
    return page


def enrich(page, records):
    return [
        detail_panel.enrich_business(
            page, item["href"], item["business"], item["identity"]
        )
        for item in records
    ]


def test_recycled_first_card_is_recovered_by_exact_href(monkeypatch):
    page = setup(monkeypatch)
    records = result_list.extract_businesses(page, 2)
    assert page.batch == 1
    assert [item["business"].name for item in records] == ["A", "B"]
    businesses = enrich(page, records)
    assert [business.address for business in businesses] == ["A address", "B address"]
    assert page.clicked == [item["href"] for item in records]


def test_failed_recovery_keeps_summary_and_does_not_click_wrong_card(monkeypatch):
    page = setup(monkeypatch, recovery_enabled=False)
    records = result_list.extract_businesses(page, 2)
    businesses = enrich(page, records)
    assert [business.name for business in businesses] == ["A", "B"]
    assert businesses[0].address is None
    assert page.clicked == [records[1]["href"]]


def test_recycled_feed_reaches_website_email_stage(monkeypatch):
    page = setup(monkeypatch)
    records = result_list.extract_businesses(page, 2)
    businesses = enrich(page, records)
    inspected = []

    class WebsiteEngine:
        def __init__(self, browser):
            pass

        def inspect(self, url):
            inspected.append(url)
            return SimpleNamespace(
                title="Site", description="Description", language="en",
                has_contact_page=False, has_about_page=False, status_code=200,
                emails=["contact@example.test"],
            )

    monkeypatch.setattr(website_enrichment, "WebsiteEngine", WebsiteEngine)
    website_enrichment.enrich_websites(None, businesses)
    assert inspected == ["https://id_a.test", "https://id_b.test"]
    assert [business.email for business in businesses] == [
        "contact@example.test", "contact@example.test"
    ]
    assert [business.address for business in businesses] == ["A address", "B address"]

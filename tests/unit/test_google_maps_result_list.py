"""Controlled virtual-feed contracts from the v0.7.1 Gate B matrix."""

import pytest

from scraper.google_maps import result_list


class Blocks:
    def count(self):
        return 0


class Article:
    def locator(self, selector):
        return Blocks()


class Link:
    def __init__(self, card):
        self.card = card

    def get_attribute(self, name):
        return self.card.get(name)

    def locator(self, selector):
        return Article()


class Links:
    def __init__(self, page):
        self.page = page

    def count(self):
        return len(self.page.cards)

    def nth(self, index):
        return Link(self.page.cards[index])


class Feed:
    def __init__(self, page):
        self.page = page

    def locator(self, selector):
        return Links(self.page)

    def hover(self):
        if self.page.hover_fails:
            raise RuntimeError("feed hover failed")


class Mouse:
    def __init__(self, page):
        self.page = page

    def wheel(self, x, y):
        self.page.wheels += 1
        self.page.batch = min(self.page.batch + 1, len(self.page.batches) - 1)


class Page:
    def __init__(self, batches, hover_fails=False):
        self.batches = batches
        self.batch = 0
        self.clock = 0.0
        self.wheels = 0
        self.hover_fails = hover_fails
        self.mouse = Mouse(self)

    @property
    def cards(self):
        return self.batches[self.batch]

    def wait_for_timeout(self, ms):
        self.clock += ms / 1000


class Selector:
    def __init__(self, page):
        self.page = page

    def selectors(self, name):
        return [name]

    def locator(self, name):
        if not self.page.cards:
            raise LookupError("legacy immediate result election")
        return Links(self.page)


def card(name, key):
    return {"aria-label": name, "href": f"/maps/place/{name}/data=!1s{key}!"}


def collect(monkeypatch, batches, limit, *, attempts=20, idle=3, seconds=30,
            hover_fails=False):
    page = Page(batches, hover_fails=hover_fails)
    monkeypatch.setattr(result_list, "create_selector_engine", lambda p: Selector(p))
    monkeypatch.setattr(
        result_list, "LazyChargeEngine",
        lambda p, profile: type("Wait", (), {"wait_feed": lambda self: Feed(p)})(),
    )
    monkeypatch.setattr(result_list.time, "monotonic", lambda: page.clock)
    monkeypatch.setattr(result_list, "MAX_SCROLL_ATTEMPTS", attempts)
    monkeypatch.setattr(result_list, "MAX_IDLE_ATTEMPTS", idle)
    monkeypatch.setattr(result_list, "MAX_LOADING_SECONDS", seconds)
    return page, lambda: result_list.extract_businesses(page, limit)


def names(results):
    return [item["business"].name for item in results]


def test_t_f01_immediate_results_do_not_scroll(monkeypatch):
    page, run = collect(monkeypatch, [[card("A", "1"), card("B", "2")]], 2)
    assert names(run()) == ["A", "B"]
    assert page.wheels == 0


def test_t_f02_progressive_equal_count_replacement(monkeypatch):
    page, run = collect(monkeypatch, [[card("A", "1")], [card("B", "2")]], 2)
    assert names(run()) == ["A", "B"]
    assert page.wheels == 1


def test_t_f03_fewer_results_at_bounded_end(monkeypatch):
    _, run = collect(monkeypatch, [[card("A", "1")]], 3)
    assert names(run()) == ["A"]


def test_t_f04_no_progress_terminates(monkeypatch):
    page, run = collect(monkeypatch, [[card("A", "1")]], 8, idle=2)
    assert names(run()) == ["A"]
    assert page.wheels <= 2


def test_t_f05_dom_batch_may_exceed_business_limit(monkeypatch):
    _, run = collect(monkeypatch, [[card("A", "1"), card("B", "2"), card("C", "3")]], 2)
    assert names(run()) == ["A", "B"]


def test_t_f06_invalid_early_candidate_does_not_consume_limit(monkeypatch):
    _, run = collect(monkeypatch, [[{"aria-label": None, "href": "x"}, card("A", "1"), card("B", "2")]], 2)
    assert names(run()) == ["A", "B"]


def test_t_f07_recycled_dom_retains_previous_summary(monkeypatch):
    _, run = collect(monkeypatch, [[card("A", "1")], [card("B", "2")], [card("C", "3")]], 3)
    assert names(run()) == ["A", "B", "C"]


def test_t_f08_scroll_failure_does_not_claim_progress(monkeypatch):
    _, run = collect(monkeypatch, [[card("A", "1")]], 3, hover_fails=True)
    with pytest.raises(RuntimeError, match="hover"):
        run()


def test_t_f09_repeated_source_candidate_keeps_first_seen_order(monkeypatch):
    _, run = collect(monkeypatch, [[card("A", "1")], [card("A", "1"), card("B", "2")]], 2)
    assert names(run()) == ["A", "B"]


@pytest.mark.parametrize("limit", [0, -3])
def test_t_f10_legacy_nonpositive_limit_still_resolves_feed(monkeypatch, limit):
    page, run = collect(monkeypatch, [[card("A", "1")]], limit)
    assert run() == []
    assert page.wheels == 0


def test_t_f11_spinner_or_scroll_activity_without_identity_is_not_progress(monkeypatch):
    page, run = collect(monkeypatch, [[card("A", "1")]] * 12, 5, idle=2)
    assert names(run()) == ["A"]
    assert page.wheels == 2


@pytest.mark.parametrize("batch,expected", [([card("A", "1")], ["A"]), ([], None)])
def test_t_f12_stall_with_and_without_valid_results(monkeypatch, batch, expected):
    _, run = collect(monkeypatch, [batch], 3, idle=2)
    if expected is None:
        with pytest.raises(LookupError):
            run()
    else:
        assert names(run()) == expected


@pytest.mark.parametrize("attempts,seconds", [(1, 30), (20, 0.5)])
def test_t_f13_attempt_and_total_time_bounds(monkeypatch, attempts, seconds):
    page, run = collect(monkeypatch, [[card("A", "1")]], 4, attempts=attempts,
                        seconds=seconds, idle=20)
    assert names(run()) == ["A"]
    assert page.wheels <= attempts


def test_t_f14_same_name_distinct_source_ids_are_not_merged(monkeypatch):
    _, run = collect(monkeypatch, [[card("Cafe", "one")], [card("Cafe", "two")], [card("Cafe", "one")]], 2)
    results = run()
    assert names(results) == ["Cafe", "Cafe"]
    assert results[0]["href"] != results[1]["href"]

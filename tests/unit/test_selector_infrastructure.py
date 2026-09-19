import pytest

from engines.selector.elector_engine import ElectorEngine
from engines.selector.registry import SelectorRegistry
from engines.selector.selector_engine import SelectorEngine


class FakeLocator:
    def __init__(self, matches):
        self.matches = matches

    def count(self):
        return self.matches


class FakePage:
    def __init__(self, counts):
        self.counts = counts

    def locator(self, selector):
        if selector == "invalid":
            raise ValueError("invalid selector")
        return FakeLocator(self.counts.get(selector, 0))


def test_registry_retrieves_known_profile_and_supports_registration():
    registry = SelectorRegistry()
    registry.register("custom", {"name": ["[data-name]"]})

    assert "google_maps" in registry.available_profiles()
    assert registry.selectors("custom", "name") == ["[data-name]"]


def test_registry_raises_for_unknown_profile_or_selector():
    registry = SelectorRegistry()

    with pytest.raises(ValueError):
        registry.profile("missing")
    with pytest.raises(ValueError):
        registry.selectors("google_maps", "missing")


def test_elector_uses_first_matching_candidate_and_optional_fallback():
    elector = ElectorEngine(FakePage({"second": 1}))

    assert elector.elect(["first", "second"]).count() == 1
    assert elector.optional(["first", "invalid"]) is None
    assert elector.exists(["second"]) is True


def test_selector_engine_resolves_semantic_names_through_registry():
    engine = SelectorEngine(FakePage({"input[name=\"q\"]": 1}), "google_maps")

    assert engine.count("search_box") == 1

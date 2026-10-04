"""Controlled validation of the owner-approved Engine limit policy."""

import pytest

from engines.config import EngineConfig, GOOGLE_MAPS_ENGINE_MAX_LIMIT, resolve_limit


def test_defaults_and_explicit_configuration_are_immutable():
    config = EngineConfig()
    assert (config.limit, config.headless, config.website_enrichment) == (50, False, True)
    with pytest.raises(AttributeError):
        config.limit = 10
    assert EngineConfig(limit=7, headless=True, website_enrichment=False).limit == 7


@pytest.mark.parametrize("kwargs", [
    {"limit": 0}, {"limit": -1}, {"limit": True}, {"limit": 3.5},
    {"headless": 1}, {"website_enrichment": "yes"},
])
def test_invalid_config_values_are_rejected(kwargs):
    with pytest.raises(ValueError):
        EngineConfig(**kwargs)


def test_requested_default_override_and_owner_maximum_are_distinct():
    config = EngineConfig(limit=5)
    assert resolve_limit(config, engine_max_limit=8) == 5
    assert resolve_limit(config, 7, engine_max_limit=8) == 7
    assert config.limit == 5


@pytest.mark.parametrize("value", [0, -1, True, 2.5, "3"])
def test_invalid_requested_limit_is_rejected(value):
    with pytest.raises(ValueError):
        resolve_limit(EngineConfig(), value, engine_max_limit=100)


def test_over_maximum_is_explicitly_rejected_without_clamping():
    with pytest.raises(ValueError, match="60 exceeds engine maximum 50"):
        resolve_limit(EngineConfig(), 60, engine_max_limit=50)


@pytest.mark.parametrize("value", [1, 50, 100])
def test_google_maps_approved_range(value):
    assert resolve_limit(
        EngineConfig(limit=value), engine_max_limit=GOOGLE_MAPS_ENGINE_MAX_LIMIT
    ) == value


def test_101_rejected_under_google_maps_policy():
    with pytest.raises(ValueError, match="maximum permitted limit is 100"):
        resolve_limit(
            EngineConfig(limit=101), engine_max_limit=GOOGLE_MAPS_ENGINE_MAX_LIMIT
        )

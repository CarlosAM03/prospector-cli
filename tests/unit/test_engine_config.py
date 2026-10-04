"""Controlled validation without inventing an operational maximum."""

import pytest

from engines.config import EngineConfig, resolve_limit


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


def test_unapproved_maximum_cannot_be_pretended_to_exist():
    with pytest.raises(RuntimeError, match="not been approved"):
        resolve_limit(EngineConfig(), engine_max_limit=None)

"""Minimal extraction configuration; operational maximum remains unsettled."""

from dataclasses import dataclass


@dataclass(frozen=True)
class EngineConfig:
    """Consumer defaults, separate from the Engine's capacity policy."""

    limit: int = 50
    headless: bool = False
    website_enrichment: bool = True

    def __post_init__(self) -> None:
        if type(self.limit) is not int or self.limit <= 0:
            raise ValueError("limit must be a positive integer")
        if type(self.headless) is not bool:
            raise ValueError("headless must be a bool")
        if type(self.website_enrichment) is not bool:
            raise ValueError("website_enrichment must be a bool")


def resolve_limit(
    config: EngineConfig,
    requested_limit: int | None = None,
    *,
    engine_max_limit: int | None,
) -> int:
    """Validate against an owner-supplied maximum; never silently clamp.

    No production maximum is supplied here. The value awaits approval from
    capacity evidence. Controlled tests may inject a numerical policy.
    """
    effective = config.limit if requested_limit is None else requested_limit
    if type(effective) is not int or effective <= 0:
        raise ValueError("requested limit must be a positive integer")
    if engine_max_limit is None:
        raise RuntimeError("engine_max_limit policy has not been approved")
    if type(engine_max_limit) is not int or engine_max_limit <= 0:
        raise ValueError("engine_max_limit must be a positive integer")
    if effective > engine_max_limit:
        raise ValueError(
            f"requested limit {effective} exceeds engine maximum {engine_max_limit}"
        )
    return effective

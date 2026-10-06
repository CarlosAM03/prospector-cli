"""Build independent normalized views with controlled field-level recovery."""

from copy import deepcopy
from dataclasses import fields
import re

from engines.issue_collector import IssueCollector
from models.business import Business
from models.normalized_business import NormalizedBusiness

from . import rules


_TRANSFORMED_FIELDS = frozenset({
    "name", "category", "address", "phone", "website", "email", "language",
})
_SAFE_POSITION = re.compile(r"business\[[0-9]+\]\Z")


class FieldUnavailable(Exception):
    """A known, recoverable field operation could not produce its value."""


class NormalizationEngine:
    """Apply approved rules without changing the source Business."""

    def normalize_business(
        self,
        business: Business,
        *,
        candidate: str | None = None,
        issue_collector: IssueCollector | None = None,
    ) -> NormalizedBusiness:
        if not isinstance(business, Business):
            raise TypeError("normalization requires Business")
        position = candidate if candidate and _SAFE_POSITION.fullmatch(candidate) else "business[?]"
        values = {}
        for field in fields(NormalizedBusiness):
            name = field.name
            original = getattr(business, name)
            if name not in _TRANSFORMED_FIELDS:
                values[name] = deepcopy(original)
                continue
            try:
                normalized = getattr(rules, f"normalize_{name}")(original)
            except FieldUnavailable as error:
                values[name] = deepcopy(original)
                self._record(issue_collector, "field_unavailable", position, name, error)
                continue
            values[name] = deepcopy(normalized)
            if name == "phone" and rules.phone_is_unverifiable(original):
                values[name] = deepcopy(original)
                self._record(issue_collector, "field_unverifiable", position, name)
        return NormalizedBusiness(**values)

    def normalize_businesses(
        self,
        businesses: list[Business],
        *,
        issue_collector: IssueCollector | None = None,
    ) -> list[NormalizedBusiness]:
        return [
            self.normalize_business(
                business, candidate=f"business[{index}]",
                issue_collector=issue_collector,
            )
            for index, business in enumerate(businesses)
        ]

    @staticmethod
    def _record(
        issue_collector: IssueCollector | None,
        code: str,
        position: str,
        field_name: str,
        error: FieldUnavailable | None = None,
    ) -> None:
        if issue_collector is not None:
            issue_collector.record(
                "normalization", code,
                candidate=f"{position}.{field_name}", error=error,
            )

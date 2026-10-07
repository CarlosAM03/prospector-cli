"""Minimal read contract shared by individual and selected batch exports."""

from dataclasses import dataclass
from typing import Protocol

from models.normalized_business import NormalizedBusiness
from models.search_query import SearchQuery


class ExportView(Protocol):
    query: SearchQuery
    businesses: list[NormalizedBusiness]


@dataclass(frozen=True)
class ExportSelection:
    query: SearchQuery
    businesses: list[NormalizedBusiness]

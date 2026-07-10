from dataclasses import dataclass, field

from models.business import Business
from models.search_query import SearchQuery


@dataclass
class SearchResult:

    query: SearchQuery

    businesses: list[Business] = field(
        default_factory=list
    )

    execution_time: float = 0.0

    @property
    def total_found(self) -> int:
        return len(self.businesses)
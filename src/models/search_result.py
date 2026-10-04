from dataclasses import dataclass, field

from models.business import Business
from models.search_query import SearchQuery
from models.search_issue import SearchIssue


@dataclass
class SearchResult:

    query: SearchQuery

    businesses: list[Business] = field(
        default_factory=list
    )

    execution_time: float = 0.0

    issues: list[SearchIssue] = field(default_factory=list)

    @property
    def total_found(self) -> int:
        return len(self.businesses)

from dataclasses import dataclass, field

from models.business import Business
from models.normalized_business import NormalizedBusiness
from models.search_query import SearchQuery
from models.search_issue import SearchIssue


@dataclass
class SearchResult:

    query: SearchQuery

    businesses: list[NormalizedBusiness] = field(
        default_factory=list
    )

    execution_time: float = 0.0

    issues: list[SearchIssue] = field(default_factory=list)

    original_businesses: list[Business] = field(default_factory=list)

    def __post_init__(self) -> None:
        if any(type(item) is not NormalizedBusiness for item in self.businesses):
            raise TypeError("businesses must contain NormalizedBusiness")
        if any(type(item) is not Business for item in self.original_businesses):
            raise TypeError("original_businesses must contain Business")
        if len(self.original_businesses) != len(self.businesses):
            raise ValueError("original and normalized counts must match")

    @property
    def total_found(self) -> int:
        return len(self.businesses)

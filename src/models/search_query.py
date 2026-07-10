from dataclasses import dataclass
from enum import Enum


class Source(str, Enum):
    GOOGLE_MAPS = "google_maps"


@dataclass
class SearchQuery:
    source: Source
    keyword: str
    location: str
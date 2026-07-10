from datetime import datetime

from models.search_query import SearchQuery


def build_output_filename(
    query: SearchQuery,
    extension: str,
) -> str:
    """
    Generate a standardized output filename.

    Example
    -------
    google_maps_maquila_tijuana_20260710_153210.xlsx
    """

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    keyword = (
        query.keyword
        .strip()
        .replace(" ", "_")
        .lower()
    )

    location = (
        query.location
        .strip()
        .replace(" ", "_")
        .lower()
    )

    source = query.source.value

    return (
        f"{source}_"
        f"{keyword}_"
        f"{location}_"
        f"{timestamp}."
        f"{extension}"
    )
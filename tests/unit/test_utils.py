import re

from models.search_query import SearchQuery, Source
from utils.file_naming import build_output_filename
from utils.parser import is_phone


def test_is_phone_accepts_selected_supported_forms():
    assert is_phone("555 123 4567") is True
    assert is_phone("555-123-4567") is True


def test_is_phone_rejects_non_phone_text():
    assert is_phone("abc") is False
    assert is_phone("") is False


def test_build_output_filename_preserves_semantic_structure_without_freezing_timestamp():
    query = SearchQuery(Source.GOOGLE_MAPS, "cafes", "Tijuana")

    filename = build_output_filename(query, "csv")

    assert re.fullmatch(r"google_maps_cafes_tijuana_\d{8}_\d{6}\.csv", filename)

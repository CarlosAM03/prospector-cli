import csv

from openpyxl import load_workbook

from models.business import Business
from models.normalized_business import NormalizedBusiness
from models.search_query import SearchQuery, Source
from models.search_result import SearchResult
from services.export_service import ExportFormat, ExportService


def make_result():
    query = SearchQuery(Source.GOOGLE_MAPS, "cafes", "Tijuana")
    return SearchResult(
        query=query,
        businesses=[
            NormalizedBusiness(
                name="EXAMPLE CAFE",
                category="CAFE",
                address="Main Street",
                phone="555 123 4567",
                email="info@example.test",
                website="https://example.test",
                language="ES",
            )
        ],
        original_businesses=[Business(
            name="Example Cafe", category="Cafe", phone="555-123-4567",
            language="es",
        )],
    )


def test_export_service_writes_expected_csv_schema(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    returned = ExportService.export(make_result(), ExportFormat.CSV)
    path = tmp_path / returned

    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.reader(handle))

    assert path.exists()
    assert rows[0] == ["Name", "Category", "Address", "Phone", "Email", "Website", "Language"]
    assert rows[1] == [
        "EXAMPLE CAFE",
        "CAFE",
        "Main Street",
        "555 123 4567",
        "info@example.test",
        "https://example.test",
        "ES",
    ]


def test_export_service_writes_readable_xlsx(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    returned = ExportService.export(make_result(), ExportFormat.EXCEL)
    path = tmp_path / returned
    workbook = load_workbook(path, read_only=True)
    try:
        rows = list(workbook["Businesses"].values)
    finally:
        workbook.close()

    assert path.exists()
    assert rows[0] == ("Name", "Category", "Address", "Phone", "Email", "Website", "Language")
    assert rows[1] == (
        "EXAMPLE CAFE", "CAFE", "Main Street", "555 123 4567",
        "info@example.test", "https://example.test", "ES",
    )
    assert len(rows) == 2

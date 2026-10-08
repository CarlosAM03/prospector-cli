"""Portable export root retains CSV/XLSX and header-only batch contracts."""

import csv
from pathlib import Path

from openpyxl import load_workbook

from models.batch import BatchQuery, BatchQueryResult, QueryStatus
from models.search_query import SearchQuery, Source
from models.search_result import SearchResult
from services._export_directory import export_directory
from services.export_service import ExportFormat, ExportService


def test_portable_header_only_batch_csv_and_xlsx(tmp_path):
    query = SearchQuery(Source.GOOGLE_MAPS, "cafe", "Tijuana")
    entry = BatchQueryResult(
        request=BatchQuery(query, 1), status=QueryStatus.SUCCESS,
        result=SearchResult(query), export_indices=[],
    )
    with export_directory(tmp_path / "portable path with spaces" / "exports"):
        csv_path = Path(ExportService.export_batch_entry(entry, ExportFormat.CSV, "a" * 32, 1))
        xlsx_path = Path(ExportService.export_batch_entry(entry, ExportFormat.EXCEL, "b" * 32, 1))
    assert csv_path.parent == xlsx_path.parent == tmp_path / "portable path with spaces" / "exports"
    with csv_path.open(newline="", encoding="utf-8") as handle:
        csv_rows = list(csv.reader(handle))
    workbook = load_workbook(xlsx_path, read_only=True)
    try:
        xlsx_rows = list(workbook["Businesses"].values)
    finally:
        workbook.close()
    expected = ["Name", "Category", "Address", "Phone", "Email", "Website", "Language"]
    assert csv_rows == [expected]
    assert xlsx_rows == [tuple(expected)]

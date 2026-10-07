from enum import Enum
from pathlib import Path
import re

from exporters.csv import CsvExporter
from exporters.excel import ExcelExporter
from exporters.export_view import ExportSelection

from models.batch import BatchQueryResult, QueryStatus
from models.search_result import SearchResult

from utils.file_naming import build_output_filename


class ExportFormat(str, Enum):
    EXCEL = "excel"
    CSV = "csv"


EXPORTERS = {

    ExportFormat.EXCEL: (
        ExcelExporter,
        "xlsx",
    ),

    ExportFormat.CSV: (
        CsvExporter,
        "csv",
    ),

}


class ExportService:

    @staticmethod
    def export(
        result: SearchResult,
        format: ExportFormat,
    ) -> str:

        exporter_class, extension = EXPORTERS[
            format
        ]

        filename = build_output_filename(
            result.query,
            extension,
        )

        exporter = exporter_class()

        exporter.export(
            result=result,
            output_path=filename,
        )

        return filename

    @staticmethod
    def export_batch_entry(
        entry: BatchQueryResult, format: ExportFormat,
        batch_id: str, query_index: int,
    ) -> str:
        """Write one valid selected view without reconstructing SearchResult."""
        if entry.status is QueryStatus.FAILED or entry.result is None:
            raise ValueError("A failed query has no exportable result.")
        if type(query_index) is not int or query_index < 1:
            raise ValueError("query_index must be a positive one-based ordinal")
        if not re.fullmatch(r"[0-9a-f]{32}", batch_id):
            raise ValueError("batch_id must be a hexadecimal operation identifier")
        exporter_class, extension = EXPORTERS[format]
        base = build_output_filename(entry.result.query, extension)
        stem = re.sub(r"[^A-Za-z0-9._-]+", "_", Path(base).stem).strip("._")
        filename = f"{stem}_{batch_id}_q{query_index:02d}.{extension}"
        selection = ExportSelection(
            entry.result.query,
            [entry.result.businesses[index] for index in entry.export_indices],
        )
        # Exclusive reservation prevents silent overwrite even with repeated queries.
        with open(filename, "x", encoding="utf-8"):
            pass
        try:
            exporter_class().export(result=selection, output_path=filename)
        except Exception:
            Path(filename).unlink(missing_ok=True)
            raise
        return filename

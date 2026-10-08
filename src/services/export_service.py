from enum import Enum
from pathlib import Path
import re

from exporters.csv import CsvExporter
from exporters.excel import ExcelExporter
from exporters.export_view import ExportSelection
from services._export_directory import active_export_directory

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

        base = re.sub(r"[^A-Za-z0-9._-]+", "_", build_output_filename(
            result.query,
            extension,
        )).strip("._")

        directory = active_export_directory()
        if directory is not None:
            directory.mkdir(parents=True, exist_ok=True)
        root = directory or Path(".")
        stem = Path(base).stem
        suffix = Path(base).suffix
        counter = 1
        while True:
            name = base if counter == 1 else f"{stem}_{counter}{suffix}"
            target = root / name
            try:
                with open(target, "x", encoding="utf-8"):
                    pass
                break
            except FileExistsError:
                counter += 1

        filename = str(target) if directory is not None else name

        exporter = exporter_class()

        try:
            exporter.export(result=result, output_path=filename)
        except Exception:
            target.unlink(missing_ok=True)
            raise

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
        name = f"{stem}_{batch_id}_q{query_index:02d}.{extension}"
        directory = active_export_directory()
        if directory is not None:
            directory.mkdir(parents=True, exist_ok=True)
        target = (directory or Path(".")) / name
        filename = str(target) if directory is not None else name
        selection = ExportSelection(
            entry.result.query,
            [entry.result.businesses[index] for index in entry.export_indices],
        )
        # Exclusive reservation prevents silent overwrite even with repeated queries.
        with open(target, "x", encoding="utf-8"):
            pass
        try:
            exporter_class().export(result=selection, output_path=filename)
        except Exception:
            target.unlink(missing_ok=True)
            raise
        return filename

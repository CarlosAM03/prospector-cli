from enum import Enum

from exporters.csv import CsvExporter
from exporters.excel import ExcelExporter

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
    
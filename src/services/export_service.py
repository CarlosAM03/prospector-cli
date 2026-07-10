from enum import Enum

from exporters.base import Exporter
from exporters.excel import ExcelExporter

from models.search_result import SearchResult


class ExportFormat(str, Enum):
    EXCEL = "excel"
    CSV = "csv"


class ExportService:

    @staticmethod
    def export(
        result: SearchResult,
        exporter: Exporter,
        output_path: str,
    ) -> None:

        exporter.export(
            result=result,
            output_path=output_path,
        )
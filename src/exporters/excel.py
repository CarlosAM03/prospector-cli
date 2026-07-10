from openpyxl import Workbook

from exporters.base import Exporter
from models.search_result import SearchResult


class ExcelExporter(Exporter):

    def export(
        self,
        result: SearchResult,
        output_path: str,
    ) -> None:

        workbook = Workbook()

        sheet = workbook.active
        sheet.title = "Businesses"

        sheet.append(
            [
                "Name",
                "Category",
                "Address",
                "Phone",
                "Email",
                "Website",
            ]
        )

        for business in result.businesses:

            sheet.append(
                [
                    business.name,
                    business.category,
                    business.address,
                    business.phone,
                    business.email,
                    business.website,
                ]
            )

        workbook.save(output_path)
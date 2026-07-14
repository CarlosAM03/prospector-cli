from openpyxl import Workbook

from exporters.base import Exporter
from models.search_result import SearchResult


class ExcelExporter(Exporter):
    """
    Excel exporter.

    Converts a SearchResult containing enriched Business
    objects into an XLSX spreadsheet.

    The exporter does not perform:

    - Extraction.
    - Validation.
    - Enrichment.
    """

    def export(
        self,
        result: SearchResult,
        output_path: str,
    ) -> None:
        """
        Export businesses into Excel format.

        Parameters
        ----------
        result:
            Completed search result.

        output_path:
            Destination XLSX file.
        """


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
                "Language",
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
                    business.language,
                ]
            )


        workbook.save(
            output_path
        )
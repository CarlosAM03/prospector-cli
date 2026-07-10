import csv

from exporters.base import Exporter
from models.search_result import SearchResult


class CsvExporter(Exporter):

    def export(
        self,
        result: SearchResult,
        output_path: str,
    ) -> None:

        with open(
            output_path,
            "w",
            newline="",
            encoding="utf-8",
        ) as file:

            writer = csv.writer(file)

            writer.writerow(
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

                writer.writerow(
                    [
                        business.name,
                        business.category,
                        business.address,
                        business.phone,
                        business.email,
                        business.website,
                    ]
                )
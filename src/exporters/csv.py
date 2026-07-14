import csv

from exporters.base import Exporter
from models.search_result import SearchResult


class CsvExporter(Exporter):
    """
    CSV exporter.

    Converts a SearchResult containing enriched Business
    objects into a structured CSV file.

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
        Export businesses into CSV format.

        Parameters
        ----------
        result:
            Completed search result.

        output_path:
            Destination CSV file.
        """


        with open(
            output_path,
            "w",
            newline="",
            encoding="utf-8",
        ) as file:

            writer = csv.writer(
                file
            )


            writer.writerow(
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

                writer.writerow(
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
from abc import ABC, abstractmethod

from exporters.export_view import ExportView


class Exporter(ABC):
    """
    Base interface for all export engines.

    Exporters are responsible for transforming a normalized
    SearchResult into a supported output format.

    Exporters never perform extraction, validation or
    deduplication.
    """

    @abstractmethod
    def export(
        self,
        result: ExportView,
        output_path: str,
    ) -> None:
        """
        Export a SearchResult to the specified output file.

        Parameters
        ----------
        result:
            Normalized search result produced by the pipeline.

        output_path:
            Destination file path.
        """

        raise NotImplementedError

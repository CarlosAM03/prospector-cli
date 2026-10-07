from models.search_query import (
    SearchQuery,
    Source,
)
from models.batch import BatchQuery, QueryStatus
from uuid import uuid4

from engines.config import EngineConfig, GOOGLE_MAPS_ENGINE_MAX_LIMIT
from engines.errors import BatchInterruptedError, ProspectorError
from engines.prospector_engine import ProspectorEngine

from services.export_service import (
    ExportFormat,
    ExportService,
)


def separator() -> None:

    print("=" * 70)


def print_business(
    index,
    business,
) -> None:

    print(
        f"[{index}] {business.name}"
    )

    print(
        "  Business Data"
    )

    print(
        f"    Category : "
        f"{business.category or '-'}"
    )

    print(
        f"    Address  : "
        f"{business.address or '-'}"
    )

    print(
        f"    Phone    : "
        f"{business.phone or '-'}"
    )

    print(
        f"    Email    : "
        f"{business.email or '-'}"
    )

    print(
        f"    Website  : "
        f"{business.website or '-'}"
    )

    print(
        f"    Language : "
        f"{business.language or '-'}"
    )

    separator()


def choose_export_format() -> ExportFormat | None:

    print()

    separator()

    print(
        "Export Options"
    )

    separator()

    print(
        "1) Excel (.xlsx)"
    )

    print(
        "2) CSV (.csv)"
    )

    print(
        "3) Skip export"
    )


    option = input(
        "\nSelection > "
    ).strip()


    if option == "1":

        return ExportFormat.EXCEL


    if option == "2":

        return ExportFormat.CSV


    if option == "3":

        return None


    print(
        "\nInvalid option."
    )

    return None



def choose_main_option() -> str:

    separator()

    print(
        "Prospector CLI"
    )

    print(
        "Google Maps Scraper"
    )

    separator()

    print(
        "1) New Search"
    )

    print(
        "2) Multiple Searches"
    )

    print(
        "3) Exit"
    )


    return input(
        "\nSelection > "
    ).strip()


def parse_requested_limit(raw: str) -> int:
    """Parse CLI input; Engine owns the separate maximum policy."""
    value = raw.strip()
    if not value:
        return 50
    if not value.isdecimal() or int(value) <= 0:
        raise ValueError("Limit must be a positive whole number.")
    if int(value) > GOOGLE_MAPS_ENGINE_MAX_LIMIT:
        raise ValueError(
            f"The maximum permitted limit is {GOOGLE_MAPS_ENGINE_MAX_LIMIT}."
        )
    return int(value)



def execute_search() -> None:

    keyword = input(
        "Keyword  : "
    ).strip()


    location = input(
        "Location : "
    ).strip()

    limit_text = input(
        "Limit (default 50, maximum 100) : "
    )


    print()


    query = SearchQuery(
        source=Source.GOOGLE_MAPS,
        keyword=keyword,
        location=location,
    )


    try:
        limit = parse_requested_limit(limit_text)
        result = ProspectorEngine(EngineConfig(limit=limit)).search(query)
    except (ValueError, ProspectorError) as error:
        print(f"Search could not start: {error}")
        return


    separator()

    print(
        "Execution Summary"
    )

    separator()


    print(
        f"Businesses Found : "
        f"{result.total_found}"
    )


    print(
        f"Execution Time   : "
        f"{result.execution_time:.2f} seconds"
    )

    print(
        f"Recoverable Issues: {len(result.issues)}"
    )

    for issue in result.issues:
        context = (
            f" ({issue.candidate})"
            if issue.stage == "normalization" and issue.candidate else ""
        )
        print(f"  {issue.stage}/{issue.code}{context}: {issue.message}")


    separator()


    for index, business in enumerate(
        result.businesses,
        start=1,
    ):

        print_business(
            index,
            business,
        )


    export_format = choose_export_format()


    if export_format is None:

        print()

        separator()

        print(
            "Search completed without export."
        )

        separator()

        return


    filename = ExportService.export(
        result=result,
        format=export_format,
    )


    print()

    separator()

    print(
        "Export Complete"
    )

    separator()

    print(
        filename
    )

    separator()



def _capture_batch_query(ordinal: int) -> BatchQuery:
    print(f"Search {ordinal}")
    keyword = input("Keyword  : ").strip()
    location = input("Location : ").strip()
    limit = parse_requested_limit(input("Limit (default 50, maximum 100) : "))
    return BatchQuery(SearchQuery(Source.GOOGLE_MAPS, keyword, location), limit)


def execute_multiple_searches() -> None:
    """Collect and confirm two or three requests before starting the Engine."""
    try:
        requests = [_capture_batch_query(1), _capture_batch_query(2)]
        if input("Add a third search? (y/N) : ").strip().lower() in {"y", "yes"}:
            requests.append(_capture_batch_query(3))
    except ValueError as error:
        print(f"Batch could not start: {error}")
        return
    separator()
    print("Batch Summary")
    for ordinal, request in enumerate(requests, start=1):
        print(f"  q{ordinal:02d}: {request.query.keyword} | {request.query.location} | limit {request.limit}")
    if input("Start these searches? (y/N) : ").strip().lower() not in {"y", "yes"}:
        print("Batch cancelled before execution.")
        return

    engine = ProspectorEngine(EngineConfig())
    try:
        batch = engine.search_many(requests)
        interrupted = None
    except BatchInterruptedError as error:
        batch = error.completed
        interrupted = error
        print(
            f"Batch interrupted at q{error.interrupted_query_index + 1:02d} "
            f"({error.reason_code}); remaining queries were not run: "
            f"{', '.join(f'q{index + 1:02d}' for index in error.remaining_query_indices) or '-'}"
        )
    except ProspectorError as error:
        print(f"Batch could not start: {error}")
        return

    separator()
    print(f"Batch Execution Time: {batch.execution_time:.2f} seconds")
    print(
        f"Observed: {batch.total_observations} | Exportable: {batch.total_exportable} | "
        f"Suppressed: {batch.duplicates_suppressed} | Unverified: {batch.total_unverified}"
    )
    for ordinal, entry in enumerate(batch.entries, start=1):
        print(
            f"q{ordinal:02d} {entry.status.value}: limit {entry.request.limit}, "
            f"found {entry.observed_count}, exportable {entry.exportable_count}, "
            f"suppressed {entry.suppressed_count}, unverified "
            f"{len(entry.unverified_identity_indices)}, time {entry.execution_time:.2f}s"
        )
        if entry.status is QueryStatus.FAILED:
            print(f"  {entry.error.category}: {entry.error.message}")
            continue
        print(f"  Recoverable Issues: {len(entry.result.issues)}")
        for issue in entry.result.issues:
            print(f"  {issue.stage}/{issue.code}: {issue.message}")
        for position in entry.export_indices:
            print_business(position + 1, entry.result.businesses[position])

    export_format = choose_export_format()
    if export_format is None:
        print("Batch completed without export." if interrupted is None
              else "Completed prefix retained without export; batch remains interrupted.")
        return
    operation_id = uuid4().hex
    for ordinal, entry in enumerate(batch.entries, start=1):
        if entry.status is QueryStatus.FAILED:
            print(f"q{ordinal:02d}: no file for failed query.")
            continue
        try:
            filename = ExportService.export_batch_entry(
                entry, export_format, operation_id, ordinal,
            )
        except (OSError, ValueError) as error:
            print(f"q{ordinal:02d}: export failed; incomplete file not retained: {error}")
            continue
        print(f"q{ordinal:02d}: {filename} ({entry.suppressed_count} duplicates suppressed)")
    if interrupted is not None:
        print("Only the safe completed prefix was offered for export; batch is not complete.")


def main() -> None:

    while True:

        option = choose_main_option()


        if option == "1":

            execute_search()


        elif option == "2":

            execute_multiple_searches()


        elif option == "3":

            separator()

            print(
                "Closing Prospector CLI..."
            )

            separator()

            break


        else:

            print(
                "\nInvalid option."
            )



if __name__ == "__main__":

    main()

from models.search_query import (
    SearchQuery,
    Source,
)

from scraper.google_maps.scraper import (
    search_businesses,
)

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
        "2) Exit"
    )


    return input(
        "\nSelection > "
    ).strip()



def execute_search() -> None:

    keyword = input(
        "Keyword  : "
    ).strip()


    location = input(
        "Location : "
    ).strip()


    print()


    query = SearchQuery(
        source=Source.GOOGLE_MAPS,
        keyword=keyword,
        location=location,
    )


    result = search_businesses(
        query=query,
        limit=500,
    )


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



def main() -> None:

    while True:

        option = choose_main_option()


        if option == "1":

            execute_search()


        elif option == "2":

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
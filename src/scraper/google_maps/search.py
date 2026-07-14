from models.search_query import SearchQuery

from .selectors import create_selector_engine


def create_search_page(
    browser,
    query: SearchQuery,
):

    page = browser.new_page()

    search_text = (
        f"{query.keyword} {query.location}"
    )

    url = (
        "https://www.google.com/maps/search/"
        + search_text.replace(" ", "+")
    )

    page.goto(url)

    selector = create_selector_engine(
        page
    )

    selector.locator(
        "feed"
    ).wait_for(
        state="visible",
        timeout=10000,
    )

    print(page.title())
    print(page.url)

    html = page.content()

    with open(
        "maps_debug.html",
        "w",
        encoding="utf-8",
    ) as file:

        file.write(html)

    return page
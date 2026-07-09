from .selectors import RESULT_FEED


def create_search_page(browser, query):

    page = browser.new_page()

    url = (
        "https://www.google.com/maps/search/"
        + query.replace(" ", "+")
    )

    page.goto(url)

    page.wait_for_selector(
        RESULT_FEED
    )

    print(page.title())
    print(page.url)

    html = page.content()

    with open(
        "maps_debug.html",
        "w",
        encoding="utf-8"
    ) as file:

        file.write(html)

    return page
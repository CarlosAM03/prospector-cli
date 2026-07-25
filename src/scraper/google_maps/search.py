from engines.navigation import NavigationEngine

from models.search_query import SearchQuery


def create_search_page(
    browser,
    query: SearchQuery,
):

    navigation = NavigationEngine(
        browser=browser,
        source=query.source,
    )

    page = navigation.open()

    search_text = (
        f"{query.keyword} {query.location}"
    )

    navigation.search(
        page=page,
        query=search_text,
    )

    return page
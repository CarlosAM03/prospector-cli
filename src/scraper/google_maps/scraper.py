from playwright.sync_api import sync_playwright

from .search import create_search_page
from .result_list import extract_businesses


def search_businesses(query, limit=50):

    with sync_playwright() as playwright:

        browser = playwright.chromium.launch(
            headless=False
        )

        page = create_search_page(
            browser,
            query
        )

        businesses = extract_businesses(
            page,
            limit
        )

        browser.close()

        return businesses
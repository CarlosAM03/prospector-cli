from playwright.sync_api import sync_playwright

from models.business import Business


def search_businesses(query, limit=50):

    businesses = []

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=False
        )

        page = browser.new_page()

        url = (
            "https://www.google.com/maps/search/"
            + query.replace(" ", "+")
        )

        page.goto(url)

        page.wait_for_selector(
            "div[role='feed']"
        )

        print(page.title())
        print(page.url)

        html = page.content()

        with open(
            "maps_debug.html",
            "w",
            encoding="utf-8"
        ) as f:
            f.write(html)

        feed = page.locator(
            "div[role='feed']"
        )

        print(
            "Feeds encontrados:",
            feed.count()
        )

        links = page.locator(
            "a[href*='/maps/place/']"
        )

        print(
            "Lugares encontrados:",
            links.count()
        )


        total = min(
            links.count(),
            limit
        )


        for index in range(total):

            link = links.nth(index)

            name = link.get_attribute(
                "aria-label"
            )

            if name:
                businesses.append(
                    Business(
                        name=name
                    )
                )


        print(
            "Negocios extraídos:",
            len(businesses)
        )


        browser.close()


    return businesses
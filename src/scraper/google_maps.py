from playwright.sync_api import sync_playwright


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
        html= page.content()
        
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
        # aquí iremos agregando extracción


        browser.close()


    return businesses
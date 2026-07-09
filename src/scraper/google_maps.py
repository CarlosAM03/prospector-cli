from playwright.sync_api import sync_playwright

from models.business import Business
from utils.parser import is_phone


def search_businesses(query, limit=50):

    businesses = []

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=True
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

            if index == 0:
                print(
                    link.evaluate(
                        "(element)=>element.parentElement.outerHTML"
                    )
                )


            name = link.get_attribute(
                "aria-label"
            )


            article = link.locator(
                "xpath=ancestor::div[@role='article']"
            )


            category = None
            address = None
            phone = None


            info_blocks = article.locator(
                "div.W4Efsd"
            )


            for block_index in range(info_blocks.count()):

                text = info_blocks.nth(block_index).inner_text()


                parts = [
                    item.strip()
                    for item in text.split("·")
                    if item.strip()
                ]


                for item in parts:

                    if is_phone(item):

                        phone = item

                    elif item and category is None:

                        if block_index > 0:
                            category = item


                if len(parts) >= 2:

                    possible_address = parts[-1]


                    if (
                        not is_phone(possible_address)
                        and possible_address != category
                    ):
                        address = possible_address



            if name:

                businesses.append(
                    Business(
                        name=name,
                        category=category,
                        address=address,
                        phone=phone
                    )
                )


        print(
            "Negocios extraídos:",
            len(businesses)
        )


        browser.close()


    return businesses
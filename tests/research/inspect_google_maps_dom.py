from playwright.sync_api import sync_playwright


with sync_playwright() as playwright:

    browser = playwright.chromium.launch(
        headless=False
    )

    page = browser.new_page()


    page.goto(
        "https://www.google.com/maps"
    )


    input(
        "Haz una búsqueda manual y abre un negocio. ENTER para continuar..."
    )


    print("\nMAIN ELEMENTS")
    print("=" * 60)


    elements = page.locator(
        "div[role='main']"
    )


    print(
        "Cantidad:",
        elements.count()
    )


    for i in range(
        elements.count()
    ):

        element = elements.nth(i)


        print()
        print(
            "ELEMENT",
            i
        )


        print(
            "aria-label:",
            element.get_attribute(
                "aria-label"
            )
        )


        print(
            "class:",
            element.get_attribute(
                "class"
            )
        )


    print("\nARIA LABEL ELEMENTS")
    print("=" * 60)


    labeled = page.locator(
        "[aria-label]"
    )


    for i in range(
        min(labeled.count(), 100)
    ):

        element = labeled.nth(i)

        label = element.get_attribute(
            "aria-label"
        )


        if label:

            print(
                i,
                element.evaluate(
                    "(e)=>e.tagName"
                ),
                label[:100]
            )


    input(
        "\nFinalizar..."
    )


    browser.close()
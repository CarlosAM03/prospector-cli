from playwright.sync_api import sync_playwright
import time


URL = "https://www.google.com/maps/search/restaurantes+tijuana"


def run_test():

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=False
        )

        page = browser.new_page()

        print("Abriendo Google Maps...")
        page.goto(URL)

        page.wait_for_timeout(5000)


        print("\n=== OBTENIENDO NEGOCIOS ===")

        businesses = page.locator(
            "a[href*='/maps/place/']"
        )

        count = businesses.count()

        print(f"Negocios encontrados: {count}")


        if count < 2:
            print("No hay suficientes negocios")
            browser.close()
            return


        # Guardamos dos href para probar
        hrefs = []

        for i in range(min(count, 3)):
            href = businesses.nth(i).get_attribute("href")
            hrefs.append(href)

            print(
                f"{i}: {href}"
            )


        print("\n==============================")
        print("PRIMER NEGOCIO")
        print("==============================")


        open_business(page, hrefs[0])

        first_state = capture_state(page)


        print_state(first_state)



        print("\n==============================")
        print("SEGUNDO NEGOCIO")
        print("==============================")


        open_business(page, hrefs[1])

        second_state = capture_state(page)

        print_state(second_state)

        page.evaluate("""
        () => {

            return window.__panel_reference
                ?.querySelector("h1")
                ?.textContent;

        }
        """)

        print("\n==============================")
        print("COMPARACIÓN")
        print("==============================")


        compare_states(
            first_state,
            second_state
        )


        browser.close()



def open_business(page, href):

    print("Abriendo:", href)


    locator = page.locator(
        f"a[href='{href}']"
    )


    locator.click()

    page.wait_for_timeout(3000)



def capture_state(page):

    state = {}

    # 1 URL

    state["url"] = page.evaluate(
        "location.href"
    )


    # 2 h1

    state["title"] = page.evaluate(
        """
        () => {

        const titles =
        [...document.querySelectorAll("h1")]
        .map(x => x.textContent);

        return titles;

        }
        """
    )


    # 3 botón dirección

    state["address_button"] = page.evaluate(
        """
        () => {
            const el =
            document.querySelector(
                "button[data-item-id='address']"
            );

            return {
                exists: !!el,
                text: el?.textContent || null
            }
        }
        """
    )


    # 4 referencia del panel

    state["panel_id_before"] = page.evaluate(
        """
        () => {

            const panel =
            document.querySelector(
                "div[role='main']"
            );

            if(!panel)
                return null;


            window.__panel_reference = panel;


            return true;
        }
        """
    )


    # Esperamos cambio

    page.wait_for_timeout(1000)


    state["same_panel"] = page.evaluate(
        """
        () => {

            return window.__panel_reference ===
            document.querySelector(
                "div[role='main']"
            );

        }
        """
    )


    return state



def print_state(state):

    print("\nURL:")
    print(state["url"][:150])


    print("\nTítulo:")
    print(state["title"])


    print("\nBotón dirección:")
    print(state["address_button"])


    print("\n¿Mismo panel?")
    print(state["same_panel"])



def compare_states(a,b):

    print(
        "URL cambió:",
        a["url"] != b["url"]
    )

    print(
        "Título cambió:",
        a["title"] != b["title"]
    )

    print(
        "Panel persistió:",
        b["same_panel"]
    )



if __name__ == "__main__":
    run_test()
from playwright.sync_api import sync_playwright

from engines.website import WebsiteEngine


def main() -> None:

    url = input(
        "Website URL: "
    ).strip()

    with sync_playwright() as playwright:

        browser = playwright.chromium.launch(
            headless=False,
        )

        engine = WebsiteEngine(
            browser
        )

        metadata = engine.inspect(
            url
        )

        browser.close()

    print()

    print("Website Metadata")
    print("----------------------------")
    print(f"Title: {metadata.title}")
    print(f"Description: {metadata.description}")
    print(f"Language: {metadata.language}")
    print(f"Domain: {metadata.domain}")
    print(f"Final URL: {metadata.final_url}")
    print(f"Contact page: {metadata.has_contact_page}")
    print(f"About page: {metadata.has_about_page}")


if __name__ == "__main__":
    main()
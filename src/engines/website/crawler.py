"""
Website Crawler.

The Website Crawler is responsible for retrieving website
documents.

Responsibilities
----------------

- Navigate to a website URL.
- Resolve redirects.
- Capture final URL.
- Retrieve HTML content.
- Preserve HTTP status information.

The crawler does not parse HTML.

It only obtains the raw website document.
"""


from playwright.sync_api import (
    Browser,
    TimeoutError,
)

from models.website_document import WebsiteDocument


class WebsiteCrawler:
    """
    Website navigation engine.

    Parameters
    ----------

    browser:
        Playwright browser instance.
    """


    def __init__(
        self,
        browser: Browser,
    ) -> None:

        self.browser = browser


    def crawl(
        self,
        url: str,
        timeout: int = 15000,
    ) -> WebsiteDocument:
        """
        Retrieve a website document.

        Parameters
        ----------

        url:
            Website address.

        timeout:
            Maximum navigation timeout.

        Returns
        -------

        WebsiteDocument
            Raw website content.

        Raises
        ------

        TimeoutError
            When website loading exceeds timeout.
        """


        page = self.browser.new_page()


        try:

            response = page.goto(
                url,
                timeout=timeout,
                wait_until="domcontentloaded",
            )


            html = page.content()


            status_code = (
                response.status
                if response
                else 0
            )


            final_url = page.url


            return WebsiteDocument(
                url=final_url,
                html=html,
                status_code=status_code,
            )


        except TimeoutError:

            return WebsiteDocument(
                url=page.url,
                html="",
                status_code=0,
            )


        finally:

            page.close()
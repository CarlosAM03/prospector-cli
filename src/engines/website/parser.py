"""
Website Parser.

The Website Parser transforms raw HTML documents into
structured website information.

Responsibilities
----------------

- Parse HTML content.
- Extract document metadata.
- Extract links.
- Extract anchor texts.

The parser does not:

- Crawl websites.
- Perform HTTP requests.
- Extract business information.
- Modify Business objects.
"""


from bs4 import BeautifulSoup

from models.website_document import WebsiteDocument


class WebsiteParser:
    """
    HTML parsing engine.

    Parameters
    ----------

    None
    """


    def parse(
        self,
        document: WebsiteDocument,
    ) -> dict:
        """
        Parse a WebsiteDocument.

        Parameters
        ----------

        document:
            Raw website document.

        Returns
        -------

        dict
            Structured website information.
        """


        soup = BeautifulSoup(
            document.html,
            "html.parser",
        )


        return {
            "url": document.url,

            "status_code": (
                document.status_code
            ),

            "title": self._title(
                soup
            ),

            "description": self._description(
                soup
            ),

            "keywords": self._keywords(
                soup
            ),

            "language": self._language(
                soup
            ),

            "links": self._links(
                soup
            ),

            "anchors": self._anchors(
                soup
            ),
        }


    def _title(
        self,
        soup: BeautifulSoup,
    ) -> str | None:
        """
        Extract HTML title.
        """

        if soup.title:

            return soup.title.text.strip()


        return None



    def _description(
        self,
        soup: BeautifulSoup,
    ) -> str | None:
        """
        Extract meta description.
        """

        tag = soup.find(
            "meta",
            attrs={
                "name": "description"
            },
        )


        if tag:

            return tag.get(
                "content"
            )


        return None



    def _keywords(
        self,
        soup: BeautifulSoup,
    ) -> str | None:
        """
        Extract meta keywords.
        """

        tag = soup.find(
            "meta",
            attrs={
                "name": "keywords"
            },
        )


        if tag:

            return tag.get(
                "content"
            )


        return None



    def _language(
        self,
        soup: BeautifulSoup,
    ) -> str | None:
        """
        Extract document language.
        """

        html = soup.find(
            "html"
        )


        if html:

            return html.get(
                "lang"
            )


        return None



    def _links(
        self,
        soup: BeautifulSoup,
    ) -> list[str]:
        """
        Extract every hyperlink URL.
        """

        links = []


        for anchor in soup.find_all(
            "a",
            href=True,
        ):

            links.append(
                anchor["href"]
            )


        return links



    def _anchors(
        self,
        soup: BeautifulSoup,
    ) -> list[str]:
        """
        Extract visible anchor texts.
        """

        anchors = []


        for anchor in soup.find_all(
            "a",
        ):

            text = anchor.get_text(
                strip=True
            )


            if text:

                anchors.append(
                    text
                )


        return anchors
"""
Website Metadata Builder.

The Metadata Builder transforms parsed website information
into a structured WebsiteMetadata model.

Responsibilities
----------------

- Build WebsiteMetadata objects.
- Normalize metadata values.
- Extract derived website information.
- Detect common website sections.

The Metadata Builder does not:

- Crawl websites.
- Parse HTML.
- Perform HTTP requests.
"""


from urllib.parse import (
    urlparse,
)

from models.website_metadata import WebsiteMetadata



class WebsiteMetadataBuilder:
    """
    Builder responsible for creating WebsiteMetadata objects.
    """



    def build(
        self,
        data: dict,
    ) -> WebsiteMetadata:
        """
        Build WebsiteMetadata from parsed website data.

        Parameters
        ----------

        data:
            Parsed website information.

        Returns
        -------

        WebsiteMetadata
        """


        url = data.get(
            "url"
        )


        return WebsiteMetadata(

            title=self._clean(
                data.get("title")
            ),


            description=self._clean(
                data.get("description")
            ),


            language=self._clean(
                data.get("language")
            ),


            domain=self._domain(
                url
            ),


            final_url=url,


            has_contact_page=self._has_page(
                data.get("links", []),
                [
                    "contact",
                    "contacto",
                ],
            ),


            has_about_page=self._has_page(
                data.get("links", []),
                [
                    "about",
                    "about-us",
                    "nosotros",
                    "empresa",
                ],
            ),
        )



    def _clean(
        self,
        value: str | None,
    ) -> str | None:
        """
        Normalize optional string values.
        """

        if not value:

            return None


        return value.strip()



    def _domain(
        self,
        url: str | None,
    ) -> str | None:
        """
        Extract domain from URL.
        """

        if not url:

            return None


        parsed = urlparse(
            url
        )


        return parsed.netloc



    def _has_page(
        self,
        links: list[str],
        keywords: list[str],
    ) -> bool:
        """
        Detect whether a website contains
        a common internal section.
        """


        for link in links:

            normalized = (
                link
                .lower()
            )


            for keyword in keywords:

                if keyword in normalized:

                    return True


        return False
"""
Website Metadata Builder.

The Metadata Builder creates WebsiteMetadata objects from
already extracted website information.

Responsibilities
----------------

- Build WebsiteMetadata instances.
- Normalize optional values.
- Extract the website domain.

The Metadata Builder does not:

- Crawl websites.
- Parse HTML.
- Detect languages.
- Search for contact pages.
- Extract emails.
"""


from urllib.parse import urlparse

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
        Build a WebsiteMetadata instance.

        Parameters
        ----------
        data:
            Already extracted website information.

        Returns
        -------
        WebsiteMetadata
        """

        url = data.get("url")

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

            has_contact_page=data.get(
                "has_contact_page",
                False,
            ),

            has_about_page=data.get(
                "has_about_page",
                False,
            ),
            status_code=data.get(
                "status_code"
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

        return urlparse(url).netloc
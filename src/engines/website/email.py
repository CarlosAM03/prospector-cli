"""
Email Extractor.

The Email Extractor is responsible for discovering email
addresses contained in a website.

Current Strategy
----------------

The initial implementation extracts email addresses from the
parsed website information produced by the Website Parser.

Future versions may extend extraction using:

- Contact pages.
- Mailto links.
- Structured data.
- JavaScript rendered content.
- Pattern normalization.
- Email validation.

The extractor never crawls websites or parses HTML directly.

It operates exclusively on parsed website data.
"""

import re


EMAIL_PATTERN = re.compile(
    r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"
)


class EmailExtractor:
    """
    Website email extraction engine.
    """

    def extract(
        self,
        parsed: dict,
    ) -> list[str]:
        """
        Extract email addresses from parsed website data.

        Parameters
        ----------
        parsed:
            Parsed website information.

        Returns
        -------
        list[str]
            Unique email addresses.
        """

        emails: set[str] = set()

        #
        # Search every parsed text source.
        #

        self._collect(
            parsed.get("anchors", []),
            emails,
        )

        self._collect(
            parsed.get("links", []),
            emails,
        )

        self._collect(
            [
                parsed.get("description"),
                parsed.get("keywords"),
                parsed.get("title"),
            ],
            emails,
        )

        return sorted(
            emails
        )

    def _collect(
        self,
        values,
        emails: set[str],
    ) -> None:
        """
        Search email addresses inside a collection
        of text values.
        """

        for value in values:

            if not value:
                continue

            matches = EMAIL_PATTERN.findall(
                value
            )

            for email in matches:

                emails.add(
                    email.lower()
                )
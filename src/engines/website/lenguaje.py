"""
Language Detector.

The Language Detector is responsible for determining the primary
language of a website.

Current Strategy
----------------

The initial implementation relies on the HTML language attribute
already extracted by the Website Parser.

Future versions may improve language detection using:

- Content analysis.
- Stop-word frequency.
- Language detection libraries.
- AI-based classification.

The detector never crawls websites or parses HTML directly.

It operates exclusively on parsed website data.
"""


class LanguageDetector:
    """
    Website language detection engine.
    """

    def detect(
        self,
        parsed: dict,
    ) -> str | None:
        """
        Detect the primary language of a website.

        Parameters
        ----------
        parsed:
            Parsed website information.

        Returns
        -------
        str | None
            ISO language code when available.
        """

        language = parsed.get(
            "language"
        )

        if not language:

            return None

        return language.strip()
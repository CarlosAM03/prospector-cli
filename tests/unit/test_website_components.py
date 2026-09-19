from engines.website.email import EmailExtractor
from engines.website.extractor import WebsiteExtractor
from engines.website.lenguaje import LanguageDetector
from engines.website.metadata import WebsiteMetadataBuilder
from engines.website.parser import WebsiteParser
from models.website_document import WebsiteDocument


HTML = """
<html lang="es">
  <head>
    <title> Example title </title>
    <meta name="description" content="Example description">
    <meta name="keywords" content="school, education">
  </head>
  <body>
    <a href="mailto:INFO@EXAMPLE.TEST">Info@example.test</a>
    <a href="https://example.test/contact">Contact</a>
  </body>
</html>
"""


def test_website_parser_extracts_metadata_links_and_anchor_text():
    document = WebsiteDocument("https://example.test", HTML, 200)

    parsed = WebsiteParser().parse(document)

    assert parsed["title"] == "Example title"
    assert parsed["description"] == "Example description"
    assert parsed["keywords"] == "school, education"
    assert parsed["language"] == "es"
    assert "https://example.test/contact" in parsed["links"]
    assert "Info@example.test" in parsed["anchors"]


def test_metadata_builder_trims_values_and_maps_url_status_and_flags():
    data = {
        "url": "https://Example.TEST/path",
        "title": "  Title  ",
        "description": " Description ",
        "language": " es ",
        "status_code": 201,
        "has_contact_page": True,
        "has_about_page": True,
    }

    metadata = WebsiteMetadataBuilder().build(data)

    assert metadata.title == "Title"
    assert metadata.description == "Description"
    assert metadata.language == "es"
    assert metadata.domain == "Example.TEST"
    assert metadata.final_url == data["url"]
    assert metadata.status_code == 201
    assert metadata.has_contact_page is True
    assert metadata.has_about_page is True


def test_language_detector_returns_trimmed_html_language():
    assert LanguageDetector().detect({"language": " es "}) == "es"
    assert LanguageDetector().detect({"language": None}) is None


def test_email_extractor_normalizes_deduplicates_and_sorts():
    parsed = {
        "anchors": ["INFO@EXAMPLE.TEST", "support@example.test"],
        "links": ["mailto:info@example.test"],
        "description": "Support@example.test",
        "keywords": None,
        "title": None,
    }

    assert EmailExtractor().extract(parsed) == ["info@example.test", "support@example.test"]


def test_website_extractor_composes_metadata_language_and_email():
    parsed = WebsiteParser().parse(WebsiteDocument("https://example.test", HTML, 200))

    metadata = WebsiteExtractor().extract(parsed)

    assert metadata.title == "Example title"
    assert metadata.language == "es"
    assert metadata.emails == ["info@example.test"]
    assert metadata.status_code == 200

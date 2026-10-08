"""Keep the product version in one importable source."""

from version import __version__


def test_product_version_for_v1_release_candidate():
    assert __version__ == "1.0.0"

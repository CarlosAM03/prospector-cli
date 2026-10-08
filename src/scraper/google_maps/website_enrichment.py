"""Optional website enrichment for already identified Maps Businesses."""

import logging

from playwright.sync_api import Browser

from engines.website.website_engine import WebsiteEngine
from engines._observability import ExecutionEvent, emit
from models.business import Business

logger = logging.getLogger(__name__)


def enrich_websites(
    browser: Browser, businesses: list[Business], issue_collector=None
) -> list[Business]:
    engine = WebsiteEngine(browser)
    for index, business in enumerate(businesses, 1):
        if not business.website:
            emit(ExecutionEvent("progress_updated", "website", current=index, total=len(businesses)))
            continue
        try:
            metadata = engine.inspect(business.website)
            _merge_metadata(business, metadata)
        except Exception as error:
            # Optional inspection must not invalidate acquired Maps data or
            # prevent the next Business from being inspected.
            logger.warning(
                "Website enrichment unavailable: %s", type(error).__name__,
            )
            if issue_collector is not None:
                issue_collector.record(
                    "website", "inspection_unavailable",
                    error=error,
                )
            emit(ExecutionEvent("progress_updated", "website", current=index, total=len(businesses)))
            continue
        emit(ExecutionEvent("progress_updated", "website", current=index, total=len(businesses)))
    return businesses


def _merge_metadata(business: Business, metadata) -> None:
    """Stage all values before mutating Business."""
    emails = metadata.emails
    values = {
        "website_title": metadata.title,
        "website_description": metadata.description,
        "language": metadata.language,
        "has_contact_page": metadata.has_contact_page,
        "has_about_page": metadata.has_about_page,
        "website_status": metadata.status_code,
        "email": emails[0] if emails else None,
    }
    for field, value in values.items():
        if value is not None and value != "":
            setattr(business, field, value)

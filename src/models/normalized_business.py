"""Independent presentation of a consolidated source Business."""

from dataclasses import dataclass


@dataclass
class NormalizedBusiness:
    name: str
    category: str | None = None
    address: str | None = None
    phone: str | None = None
    website: str | None = None
    email: str | None = None
    language: str | None = None
    website_title: str | None = None
    website_description: str | None = None
    has_contact_page: bool | None = None
    has_about_page: bool | None = None
    website_status: int | None = None

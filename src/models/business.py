from dataclasses import dataclass


@dataclass
class Business:
    name: str
    category: str | None = None
    address: str | None = None
    phone: str | None = None
    email: str | None = None
    website: str | None = None
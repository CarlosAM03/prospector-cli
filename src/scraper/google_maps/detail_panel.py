from models.business import Business


def enrich_business(page, business: Business) -> Business:
    """
    Enriches a Business entity using the Google Maps
    business detail panel.

    v0.3 implementation pending.
    """

    return business
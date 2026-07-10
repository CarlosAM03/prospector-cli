"""
Google Maps selectors.

"""

RESULT_FEED = "div[role='feed']"

RESULT_LINK = "a[href*='/maps/place/']"

RESULT_ARTICLE = "xpath=ancestor::div[@role='article']"

INFO_BLOCK = "div.W4Efsd"

# Detail panel

DETAIL_PANEL = "div[role='main']"

ADDRESS_BUTTON = "button[data-item-id='address']"

ADDRESS_TEXT = (
    "button[data-item-id='address'] .Io6YTe"
)

WEBSITE_LINK = (
    "a[data-item-id='authority']"
)

PHONE_LINK = (
    "a[data-item-id^='phone:']"
)

PHONE_TEXT = (
    "a[data-item-id^='phone:'] .Io6YTe"
)
"""
Selector profiles.

A selector profile contains every DOM selector required by a
specific scraper implementation.

Profiles are intentionally isolated from the scraper logic so
selectors can evolve independently from extraction algorithms.

Every selector is identified by a semantic name instead of a
CSS selector.

Example:

feed
results
phone
website

instead of

div[role='feed']
a[data-item-id='authority']

Future scrapers may provide their own selector profiles while
reusing the same Selector Engine.
"""


GOOGLE_MAPS_PROFILE = {

    #
    # Search results
    #

    "feed": [

        "div[role='feed']",

    ],

    "results": [

        "a[href*='/maps/place/']",

    ],

    "result_article": [

        "xpath=ancestor::div[@role='article']",

    ],

    "info_block": [

        "div.W4Efsd",

    ],

    #
    # Detail panel
    #

    "detail_panel": [

        "div[role='main']",

    ],

    "business_name": [

        "h1",

    ],

    "address_button": [

        "button[data-item-id='address']",

    ],

    "address": [

        "button[data-item-id='address'] .Io6YTe",

    ],

    "phone": [

        "a[data-item-id^='phone:'] .Io6YTe",

    ],

    "website": [

        "a[data-item-id='authority']",

    ],

}
"""
Selector profiles.

A selector profile contains every DOM selector required by a
specific scraper implementation.

Profiles are intentionally isolated from scraper logic so
selectors can evolve independently from extraction algorithms.

Every selector is identified by a semantic name instead of a
CSS selector.

Future scraper improvements should extend selector profiles
instead of introducing raw CSS selectors throughout the codebase.
"""

GOOGLE_MAPS_PROFILE = {

    #
    # Navigation
    #

    "home_logo": [
        "a[aria-label='Google Maps']",
    ],

    "search_box": [
        "input#searchboxinput",
    ],

    "search_button": [
        "button#searchbox-searchbutton",
    ],

    #
    # Search page
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
    # Lazy loading
    #

    "loading": [
        "div[role='progressbar']",
    ],

    "spinner": [
        "div[role='progressbar']",
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
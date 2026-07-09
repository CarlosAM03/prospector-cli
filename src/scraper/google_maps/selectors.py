"""
Google Maps selectors.

Todos los selectores específicos de Google Maps deben
centralizarse en este archivo para facilitar su mantenimiento.
"""

RESULT_FEED = "div[role='feed']"

RESULT_LINK = "a[href*='/maps/place/']"

RESULT_ARTICLE = "xpath=ancestor::div[@role='article']"

INFO_BLOCK = "div.W4Efsd"
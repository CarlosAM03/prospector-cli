"""Pure, conservative presentation rules for consolidated Business fields."""

import re


_LOCAL_PHONE = re.compile(
    r"(?:\([0-9]{3}\)|[0-9]{3})[ .-]?[0-9]{3}[ .-]?[0-9]{4}\Z"
)
_EXPLICIT_ONE_PHONE = re.compile(
    r"\+1[ .-]?(?:\([0-9]{3}\)|[0-9]{3})[ .-]?[0-9]{3}[ .-]?[0-9]{4}\Z"
)
_EXTENSION = re.compile(r"\b(?:ext\.?|extension|x)\s*[0-9a-z]+\b", re.IGNORECASE)


def _presentation_text(value: str | None) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise TypeError("normalization requires a string or None")
    collapsed = " ".join(value.split())
    return collapsed if collapsed else value


def normalize_name(value: str) -> str:
    return _presentation_text(value).upper()


def normalize_category(value: str | None) -> str | None:
    cleaned = _presentation_text(value)
    return cleaned.upper() if cleaned is not None else None


def normalize_address(value: str | None) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise TypeError("address must be a string or None")
    cleaned = value.strip()
    return cleaned if cleaned else value


def normalize_phone(value: str | None) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise TypeError("phone must be a string or None")
    candidate = value.strip()
    if _EXTENSION.search(candidate):
        return value
    if _LOCAL_PHONE.fullmatch(candidate):
        digits = "".join(character for character in candidate if character in "0123456789")
        return f"{digits[:3]} {digits[3:6]} {digits[6:]}"
    if _EXPLICIT_ONE_PHONE.fullmatch(candidate):
        digits = "".join(character for character in candidate if character in "0123456789")
        return f"+1 {digits[1:4]} {digits[4:7]} {digits[7:]}"
    return value


def phone_is_unverifiable(value: str | None) -> bool:
    """A present phone-like value could not use a safe approved format."""
    if value is None or not isinstance(value, str) or not value.strip():
        return False
    if _EXTENSION.search(value):
        return False  # deliberate policy preservation
    if value.strip().startswith("+"):
        return False  # other explicit international patterns are preserved by policy
    if _LOCAL_PHONE.fullmatch(value.strip()) or _EXPLICIT_ONE_PHONE.fullmatch(value.strip()):
        return False
    return True


def normalize_website(value: str | None) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise TypeError("website must be a string or None")
    cleaned = value.strip()
    return cleaned if cleaned else value


def normalize_email(value: str | None) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise TypeError("email must be a string or None")
    cleaned = value.strip()
    return cleaned.lower() if cleaned else value


def normalize_language(value: str | None) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise TypeError("language must be a string or None")
    cleaned = value.strip()
    return cleaned.upper() if cleaned else value

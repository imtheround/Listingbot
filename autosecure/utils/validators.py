"""Input validation utilities."""

from __future__ import annotations

import re


def valid_email(email: str) -> bool:
    """Validate an email address.

    Checks for a valid local part, @ symbol, and properly formatted domain.

    Args:
        email: The email address to validate.

    Returns:
        True if the email is valid.
    """
    pattern = re.compile(
        r"^[a-zA-Z0-9]"
        r"(?:[a-zA-Z0-9._%+-]{0,62}[a-zA-Z0-9])?"
        r"@[a-zA-Z0-9]"
        r"(?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?"
        r"(?:\.[a-zA-Z]{2,})+$"
    )
    return bool(pattern.match(email))


def valid_discord_id(id_str: str) -> bool:
    """Validate a Discord snowflake ID.

    Discord snowflakes are 17-20 digit numeric strings.

    Args:
        id_str: The ID string to validate.

    Returns:
        True if the ID is a valid Discord snowflake.
    """
    return bool(re.fullmatch(r"\d{17,20}", id_str))


def valid_mc_username(username: str) -> bool:
    """Validate a Minecraft username.

    Minecraft usernames are 3-16 characters, alphanumeric and underscores only.

    Args:
        username: The username to validate.

    Returns:
        True if the username is valid.
    """
    return bool(re.fullmatch(r"[a-zA-Z0-9_]{3,16}", username))


def valid_url(url: str) -> bool:
    """Validate a URL.

    Checks for http/https scheme and valid domain format.

    Args:
        url: The URL to validate.

    Returns:
        True if the URL is valid.
    """
    pattern = re.compile(
        r"^https?://"
        r"(?:[a-zA-Z0-9]"
        r"(?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)*"
        r"[a-zA-Z]{2,}"
        r"(?::\d{1,5})?"
        r"(?:/[^\s]*)?$"
    )
    return bool(pattern.match(url))


def valid_ltc_address(address: str) -> bool:
    """Validate a Litecoin address.

    Supports legacy (L/M/3 prefix) and bech32 (ltc1 prefix) formats.

    Args:
        address: The Litecoin address to validate.

    Returns:
        True if the address is a valid Litecoin address.
    """
    legacy = re.fullmatch(r"[LM3][a-km-zA-HJ-NP-Z1-9]{26,33}", address)
    bech32 = re.fullmatch(r"ltc1[a-zA-HJ-NP-Z0-9]{25,39}", address)
    return bool(legacy or bech32)


def valid_recovery_code(code: str) -> bool:
    """Validate a recovery code in the format XXXXX-XXXXX-XXXXX-XXXXX-XXXXX.

    Args:
        code: The recovery code to validate.

    Returns:
        True if the code matches the expected format.
    """
    return bool(re.fullmatch(r"[A-Z0-9]{5}(-[A-Z0-9]{5}){4}", code))


def valid_otp(otp: str) -> bool:
    """Validate a one-time password (6 or 7 digits).

    Args:
        otp: The OTP code to validate.

    Returns:
        True if the OTP is 6 or 7 digits.
    """
    return bool(re.fullmatch(r"\d{6,7}", otp))

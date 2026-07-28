"""Text utilities for Discord formatting and extraction."""

from __future__ import annotations

import re


def codeblock(text: str, lang: str = "") -> str:
    """Wrap text in a Discord markdown codeblock.

    Args:
        text: The text content.
        lang: Optional language for syntax highlighting.

    Returns:
        The text wrapped in triple backticks.
    """
    return f"```{lang}\n{text}\n```"


def extract_verification_code(text: str) -> str | None:
    """Extract a 6 or 7 digit verification code from email text.

    Searches for standalone numeric codes of 6-7 digits, optionally
    surrounded by whitespace or common separators.

    Args:
        text: The email body text to search.

    Returns:
        The first matching code string, or None if not found.
    """
    match = re.search(r"(?:^|\s)(\d{6,7})(?:\s|$|[.,;:!?])", text)
    if match:
        return match.group(1)

    match = re.search(r"\b(\d{6,7})\b", text)
    if match:
        return match.group(1)

    return None


def truncate(text: str, max_length: int = 4096) -> str:
    """Truncate text to fit within Discord's embed character limit.

    Appends an ellipsis if truncation occurs.

    Args:
        text: The text to truncate.
        max_length: Maximum allowed character count (default 4096).

    Returns:
        The text, truncated if necessary.
    """
    if len(text) <= max_length:
        return text
    return text[: max_length - 1] + "\u2026"

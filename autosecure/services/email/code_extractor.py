"""Verification code extraction from email text."""

from __future__ import annotations

import re

from autosecure.core.logging import get_logger

log = get_logger("email.code_extractor")

CODE_PATTERNS = [
    re.compile(r"(?:verification|code|otp|pin|token|confirm)[^\d]*(\d{6,7})", re.IGNORECASE),
    re.compile(r"(\d{6,7})[^\w]*(?:verification|code|otp|pin|token|confirm)", re.IGNORECASE),
    re.compile(r"(?:^|\s)(\d{6,7})(?:\s|$)", re.MULTILINE),
    re.compile(r"[:\s](\d{6,7})"),
    re.compile(r"(\d{6,7})"),
]


def extract_code(text: str) -> str | None:
    """Extract a 6-7 digit verification code from text.

    Uses multiple regex strategies in priority order:
    1. Code near keywords (verification, code, otp, etc.)
    2. Code followed by keywords
    3. Standalone code on its own line
    4. Code after colon or whitespace
    5. Fallback: first 6-7 digit number found

    Args:
        text: The text to search for a verification code.

    Returns:
        The extracted code as a string, or None if not found.
    """
    if not text:
        return None

    for pattern in CODE_PATTERNS:
        match = pattern.search(text)
        if match:
            code = match.group(1)
            if _is_valid_code(code):
                log.debug("code_extractor.found", code=code, pattern=pattern.pattern)
                return code

    return None


def _is_valid_code(code: str) -> bool:
    """Validate that a code looks like a real verification code.

    Args:
        code: The code string to validate.

    Returns:
        True if the code is a valid 6-7 digit number.
    """
    if not code.isdigit():
        return False
    if len(code) < 6 or len(code) > 7:
        return False
    return not (code == "000000" or code == "0000000")

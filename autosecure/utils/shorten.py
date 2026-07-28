"""Number shortening utilities."""

from __future__ import annotations


def shorten_number(n: float) -> str:
    """Shorten a number with a suffix (K, M, B, T).

    Uses one decimal place. Examples:
        1234567 -> "1.2M"
        1234 -> "1.2K"
        999 -> "999"
        1500000000 -> "1.5B"

    Args:
        n: The number to shorten.

    Returns:
        A shortened string representation.
    """
    abs_n = abs(n)
    sign = "-" if n < 0 else ""

    if abs_n >= 1_000_000_000_000:
        return f"{sign}{abs_n / 1_000_000_000_000:.1f}T"
    if abs_n >= 1_000_000_000:
        return f"{sign}{abs_n / 1_000_000_000:.1f}B"
    if abs_n >= 1_000_000:
        return f"{sign}{abs_n / 1_000_000:.1f}M"
    if abs_n >= 1_000:
        return f"{sign}{abs_n / 1_000:.1f}K"
    return f"{sign}{abs_n:.0f}"

"""Color generation utilities."""

from __future__ import annotations

import random


def random_color() -> int:
    """Generate a random color as an integer (0x000000 - 0xFFFFFF).

    Returns:
        A random integer suitable for use as a Discord embed color.
    """
    return random.randint(0, 0xFFFFFF)


def random_color_hex() -> str:
    """Generate a random color as a hex string in '#RRGGBB' format.

    Returns:
        A random hex color string like '#3A9F0B'.
    """
    return f"#{random.randint(0, 0xFFFFFF):06X}"

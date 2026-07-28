"""Random string and UID generation utilities."""

from __future__ import annotations

import random
import string


def generate_string(length: int = 8, first_letter: bool = True) -> str:
    """Generate a random alphanumeric string.

    Args:
        length: Length of the output string.
        first_letter: If True, the first character is guaranteed to be a letter.

    Returns:
        A random alphanumeric string.
    """
    if length < 1:
        raise ValueError("length must be at least 1")

    if first_letter:
        first = random.choice(string.ascii_letters)
        rest = "".join(random.choices(string.ascii_letters + string.digits, k=length - 1))
        return first + rest

    return "".join(random.choices(string.ascii_letters + string.digits, k=length))


def generate_uid(length: int = 9) -> str:
    """Generate a random alphanumeric UID.

    Args:
        length: Length of the UID.

    Returns:
        A random alphanumeric UID string.
    """
    return generate_string(length=length, first_letter=False)


def generate_uid_hex(length: int = 16) -> str:
    """Generate a random hexadecimal UID string.

    Args:
        length: Number of hex characters.

    Returns:
        A lowercase hex string.
    """
    return "".join(random.choices(string.hexdigits[:16], k=length))

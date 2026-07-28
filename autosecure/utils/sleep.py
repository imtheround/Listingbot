"""Async sleep utility."""

from __future__ import annotations

import asyncio


async def sleep(seconds: float) -> None:
    """Sleep for the specified number of seconds.

    Args:
        seconds: Number of seconds to sleep. Must be non-negative.
    """
    if seconds < 0:
        raise ValueError("seconds must be non-negative")
    await asyncio.sleep(seconds)

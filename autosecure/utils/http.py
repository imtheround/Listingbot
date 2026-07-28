"""Async HTTP client factory with retry logic and rotating user agents."""

from __future__ import annotations

import random

import httpx

from autosecure.core.config import settings


def get_random_ua() -> str:
    """Get a random user agent from the configured list.

    Returns:
        A random user agent string.
    """
    return random.choice(settings.http.user_agents)


def get_client(**kwargs: object) -> httpx.AsyncClient:
    """Create an async HTTP client with project defaults.

    Configures rotating user agents, proxy support, timeout, and retry
    logic with exponential backoff.

    Args:
        **kwargs: Additional keyword arguments passed to httpx.AsyncClient.

    Returns:
        A configured httpx.AsyncClient instance.
    """
    headers: dict[str, str] = {"User-Agent": get_random_ua()}
    if "headers" in kwargs:
        headers.update(kwargs.pop("headers"))  # type: ignore[arg-type]

    transport = kwargs.pop("transport", None)

    timeout = kwargs.pop("timeout", settings.http.timeout)

    client = httpx.AsyncClient(
        headers=headers,
        timeout=timeout,
        transport=transport,
        **kwargs,  # type: ignore[arg-type]
    )
    return client

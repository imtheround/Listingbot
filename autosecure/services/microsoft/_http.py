"""Shared HTTP client for Microsoft API calls."""

from __future__ import annotations

import asyncio
import random
from typing import Any

import httpx

from autosecure.core.config import settings
from autosecure.core.logging import get_logger

log = get_logger("microsoft.http")

USER_AGENTS = settings.http.user_agents

MICROSOFT_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Cache-Control": "max-age=0",
}


class MicrosoftHTTPClient:
    """Async HTTP client with retry logic, proxy support, and cookie management.

    Provides methods for Microsoft API calls with exponential backoff
    and rotating user agents.

    Usage::

        async with MicrosoftHTTPClient(proxy="http://...") as client:
            response = await client.get("https://example.com")
    """

    def __init__(
        self,
        proxy: str | None = None,
        cookies: dict[str, str] | None = None,
        timeout: int | None = None,
    ) -> None:
        """Initialize the HTTP client.

        Args:
            proxy: Optional proxy URL string (e.g. "http://user:pass@host:port").
            cookies: Optional initial cookies dict.
            timeout: Optional timeout override in seconds.
        """
        self.proxy = proxy
        self.cookies: dict[str, str] = dict(cookies) if cookies else {}
        self.timeout = timeout or settings.http.timeout
        self._client: httpx.AsyncClient | None = None

    def _build_transport(self) -> httpx.AsyncHTTPTransport | None:
        """Build an optional proxy transport."""
        if self.proxy:
            return httpx.AsyncHTTPTransport(proxy=self.proxy)
        return None

    def _build_headers(self) -> dict[str, str]:
        """Build request headers with a rotating user agent."""
        return {
            "User-Agent": random.choice(USER_AGENTS),
            **MICROSOFT_HEADERS,
        }

    async def __aenter__(self) -> MicrosoftHTTPClient:
        """Enter the async context manager and create the underlying client."""
        self._client = httpx.AsyncClient(
            headers=self._build_headers(),
            cookies=self.cookies,
            timeout=self.timeout,
            transport=self._build_transport(),
            follow_redirects=True,
        )
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: object,
    ) -> None:
        """Exit the async context manager, closing the underlying client."""
        await self.close()

    async def close(self) -> None:
        """Close the underlying HTTP client if it exists."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None

    def _ensure_client(self) -> httpx.AsyncClient:
        """Return the internal client or raise if not connected.

        Returns:
            The httpx.AsyncClient instance.

        Raises:
            RuntimeError: If used outside of an async context manager.
        """
        if self._client is None or self._client.is_closed:
            raise RuntimeError(
                "MicrosoftHTTPClient must be used as an async context manager. "
                "Use: async with MicrosoftHTTPClient() as client: ..."
            )
        return self._client

    async def _request(
        self,
        method: str,
        url: str,
        *,
        max_retries: int = 3,
        backoff_base: float = 1.0,
        **kwargs: Any,
    ) -> httpx.Response:
        """Execute an HTTP request with exponential backoff retry.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE).
            url: Target URL.
            max_retries: Maximum number of retry attempts.
            backoff_base: Base delay in seconds for exponential backoff.
            **kwargs: Additional keyword arguments passed to httpx.

        Returns:
            The httpx Response object.

        Raises:
            httpx.HTTPError: If all retries are exhausted.
        """
        client = self._ensure_client()
        last_exc: Exception | None = None

        for attempt in range(max_retries):
            try:
                response = await client.request(method, url, **kwargs)

                if response.status_code == 429:
                    retry_after = float(
                        response.headers.get("Retry-After", backoff_base * (2 ** attempt))
                    )
                    log.warning("rate_limited", url=url, retry_after=retry_after)
                    await asyncio.sleep(retry_after)
                    continue

                response.raise_for_status()
                self.cookies.update(dict(response.cookies))
                return response

            except httpx.HTTPStatusError as exc:
                if exc.response.status_code < 500:
                    raise
                last_exc = exc
            except httpx.HTTPError as exc:
                last_exc = exc

            delay = backoff_base * (2 ** attempt) + random.uniform(0, 0.5)
            log.debug("request_retry", attempt=attempt + 1, delay=delay, url=url)
            await asyncio.sleep(delay)

        raise last_exc  # type: ignore[misc]

    async def get(self, url: str, **kwargs: Any) -> httpx.Response:
        """Send a GET request."""
        return await self._request("GET", url, **kwargs)

    async def post(self, url: str, **kwargs: Any) -> httpx.Response:
        """Send a POST request."""
        return await self._request("POST", url, **kwargs)

    async def put(self, url: str, **kwargs: Any) -> httpx.Response:
        """Send a PUT request."""
        return await self._request("PUT", url, **kwargs)

    async def delete(self, url: str, **kwargs: Any) -> httpx.Response:
        """Send a DELETE request."""
        return await self._request("DELETE", url, **kwargs)

    def set_cookies(self, cookies: dict[str, str]) -> None:
        """Merge cookies into the client's cookie jar.

        Args:
            cookies: Cookies to merge.
        """
        self.cookies.update(cookies)

    def get_cookie(self, name: str) -> str | None:
        """Get a cookie value by name.

        Args:
            name: Cookie name.

        Returns:
            The cookie value, or None if not found.
        """
        return self.cookies.get(name)

    def clear_cookies(self) -> None:
        """Clear all stored cookies."""
        self.cookies.clear()

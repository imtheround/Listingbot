"""Hypixel API client with key management and rate limiting."""

from __future__ import annotations

import asyncio
import time
from typing import Any

import httpx
import structlog

from autosecure.utils.http import get_client

log = structlog.get_logger(__name__)

HYPIXEL_API_BASE = "https://api.hypixel.net"


class HypixelClient:
    """Async Hypixel API client with automatic key management."""

    def __init__(self, api_key: str | None = None) -> None:
        """Initialize the Hypixel API client.

        Args:
            api_key: Hypixel API key. If not provided, uses config default.
        """
        self._api_key = api_key or ""
        self._rate_limit_remaining = 120
        self._rate_limit_reset = 0.0
        self._last_request_time = 0.0

    @property
    def api_key(self) -> str:
        """Get the current API key."""
        return self._api_key

    def set_key(self, key: str) -> None:
        """Set the API key.

        Args:
            key: New Hypixel API key.
        """
        self._api_key = key
        log.info("hypixel.client.set_key")

    def get_key(self) -> str:
        """Get the current API key.

        Returns:
            Current API key string.
        """
        return self._api_key

    async def refresh_key(self) -> str:
        """Generate and retrieve a new API key from Hypixel.

        Returns:
            New API key string, or empty string on failure.
        """
        log.info("hypixel.client.refresh_key")

        try:
            async with get_client() as client:
                response = await client.post(
                    f"{HYPIXEL_API_BASE}/key",
                    params={"key": self._api_key},
                )

                if response.status_code == 200:
                    data = response.json()
                    new_key = data.get("key", "")
                    if new_key:
                        self._api_key = new_key
                        log.info("hypixel.client.refresh_key.success")
                        return new_key

                log.warning(
                    "hypixel.client.refresh_key.failed",
                    status=response.status_code,
                )
                return ""

        except Exception as e:
            log.error("hypixel.client.refresh_key.error", error=str(e))
            return ""

    async def _request(
        self,
        method: str,
        path: str,
        **kwargs: Any,
    ) -> dict | None:
        """Make an authenticated request to the Hypixel API.

        Handles rate limiting, retries, and error responses.

        Args:
            method: HTTP method (GET, POST, etc.).
            path: API endpoint path (e.g., "/player").
            **kwargs: Additional arguments for httpx.

        Returns:
            Response JSON as dict, or None on error.
        """
        if not self._api_key:
            log.error("hypixel.client._request.no_key")
            return None

        # Respect rate limits
        await self._wait_for_rate_limit()

        url = f"{HYPIXEL_API_BASE}{path}"
        headers = kwargs.pop("headers", {})
        headers["API-Key"] = self._api_key

        try:
            async with get_client() as client:
                response = await client.request(
                    method, url, headers=headers, **kwargs
                )

                # Update rate limit info
                self._update_rate_limit(response)

                if response.status_code == 429:
                    # Rate limited - wait and retry
                    retry_after = float(
                        response.headers.get("Retry-After", "5")
                    )
                    log.warning(
                        "hypixel.client._request.rate_limited",
                        retry_after=retry_after,
                    )
                    await asyncio.sleep(retry_after)
                    return await self._request(method, path, **kwargs)

                if response.status_code != 200:
                    log.warning(
                        "hypixel.client._request.error",
                        status=response.status_code,
                        path=path,
                    )
                    return None

                return response.json()

        except httpx.HTTPError as e:
            log.error("hypixel.client._request.http_error", error=str(e))
            return None
        except Exception as e:
            log.error("hypixel.client._request.error", error=str(e))
            return None

    async def _wait_for_rate_limit(self) -> None:
        """Wait if necessary to respect rate limits."""
        if self._rate_limit_remaining <= 1:
            wait_time = max(0, self._rate_limit_reset - time.time())
            if wait_time > 0:
                log.debug(
                    "hypixel.client.rate_limit_wait",
                    wait_seconds=wait_time,
                )
                await asyncio.sleep(wait_time)

        # Minimum delay between requests
        elapsed = time.time() - self._last_request_time
        if elapsed < 0.1:
            await asyncio.sleep(0.1 - elapsed)

    def _update_rate_limit(self, response: httpx.Response) -> None:
        """Update rate limit state from response headers."""
        try:
            remaining = response.headers.get("Rate-Limit-Remaining")
            if remaining is not None:
                self._rate_limit_remaining = int(remaining)

            reset = response.headers.get("Rate-Limit-Reset")
            if reset is not None:
                self._rate_limit_reset = float(reset)

            self._last_request_time = time.time()
        except (ValueError, TypeError):
            pass

    async def get_player(self, uuid: str) -> dict | None:
        """Get player data by UUID.

        Args:
            uuid: Player UUID (with or without dashes).

        Returns:
            Player data dict, or None if not found.
        """
        clean_uuid = uuid.replace("-", "")
        return await self._request("GET", "/player", params={"uuid": clean_uuid})

    async def get_player_by_username(self, username: str) -> dict | None:
        """Get player data by username.

        First resolves the UUID via Mojang API, then fetches Hypixel data.

        Args:
            username: Minecraft username.

        Returns:
            Player data dict, or None if not found.
        """
        from autosecure.services.minecraft.profile import get_uuid

        uuid = await get_uuid(username)
        if not uuid:
            return None
        return await self.get_player(uuid)

    async def get_recent_games(self, uuid: str) -> dict | None:
        """Get recent games for a player.

        Args:
            uuid: Player UUID.

        Returns:
            Recent games data dict, or None.
        """
        clean_uuid = uuid.replace("-", "")
        return await self._request(
            "GET", "/recentGames", params={"uuid": clean_uuid}
        )

    async def get_watchdog_stats(self) -> dict | None:
        """Get Hypixel Watchdog statistics.

        Returns:
            Watchdog stats dict, or None.
        """
        return await self._request("GET", "/watchdogstats")

    async def get_boosters(self) -> dict | None:
        """Get active server boosters.

        Returns:
            Boosters data dict, or None.
        """
        return await self._request("GET", "/boosters")

    async def get_leaderboards(self) -> dict | None:
        """Get Hypixel leaderboards.

        Returns:
            Leaderboards data dict, or None.
        """
        return await self._request("GET", "/leaderboards")

    async def get_status(self) -> dict | None:
        """Get Hypixel server status.

        Returns:
            Server status dict, or None.
        """
        return await self._request("GET", "/status")

    async def get_online(self) -> dict | None:
        """Get online player count.

        Returns:
            Online players dict, or None.
        """
        return await self._request("GET", "/online")

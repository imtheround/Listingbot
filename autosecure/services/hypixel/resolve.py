"""UUID resolution using the Mojang API."""

from __future__ import annotations

import httpx
import structlog

from autosecure.utils.http import get_client

log = structlog.get_logger(__name__)

MOJANG_API_URL = "https://api.mojang.com"
MOJANG_SESSION_URL = "https://sessionserver.mojang.com"


async def resolve_uuid(username: str) -> str | None:
    """Resolve a Minecraft username to UUID.

    Args:
        username: Minecraft username to resolve.

    Returns:
        UUID string without dashes, or None if not found.
    """
    log.info("hypixel.resolve.resolve_uuid", username=username)

    try:
        async with get_client() as client:
            response = await client.get(
                f"{MOJANG_API_URL}/users/profiles/minecraft/{username}",
            )

            if response.status_code != 200:
                log.warning(
                    "hypixel.resolve.resolve_uuid.not_found",
                    username=username,
                    status=response.status_code,
                )
                return None

            data = response.json()
            uuid = data.get("id")
            if uuid:
                log.debug(
                    "hypixel.resolve.resolve_uuid.found",
                    username=username,
                    uuid=uuid,
                )
            return uuid

    except httpx.HTTPError as e:
        log.error("hypixel.resolve.resolve_uuid.http_error", error=str(e))
        return None
    except Exception as e:
        log.error("hypixel.resolve.resolve_uuid.error", error=str(e))
        return None


async def resolve_username(uuid: str) -> str | None:
    """Resolve a Minecraft UUID to username.

    Args:
        uuid: Minecraft UUID (with or without dashes).

    Returns:
        Current username, or None if not found.
    """
    clean_uuid = uuid.replace("-", "")
    log.info("hypixel.resolve.resolve_username", uuid=clean_uuid)

    try:
        async with get_client() as client:
            response = await client.get(
                f"{MOJANG_API_URL}/user/profiles/{clean_uuid}/names",
            )

            if response.status_code != 200:
                log.warning(
                    "hypixel.resolve.resolve_username.not_found",
                    uuid=clean_uuid,
                    status=response.status_code,
                )
                return None

            data = response.json()
            if not data:
                return None

            # Last entry is the current username
            username = data[-1].get("name")
            if username:
                log.debug(
                    "hypixel.resolve.resolve_username.found",
                    uuid=clean_uuid,
                    username=username,
                )
            return username

    except httpx.HTTPError as e:
        log.error("hypixel.resolve.resolve_username.http_error", error=str(e))
        return None
    except Exception as e:
        log.error("hypixel.resolve.resolve_username.error", error=str(e))
        return None


async def resolve_usernames_bulk(
    usernames: list[str],
) -> dict[str, str | None]:
    """Resolve multiple usernames to UUIDs in batch.

    Args:
        usernames: List of usernames to resolve.

    Returns:
        Dictionary mapping usernames to UUIDs (None for failed lookups).
    """
    log.info("hypixel.resolve.resolve_usernames_bulk", count=len(usernames))

    results: dict[str, str | None] = {}

    # Process in parallel with limited concurrency
    import asyncio

    semaphore = asyncio.Semaphore(10)

    async def _resolve_one(username: str) -> tuple[str, str | None]:
        async with semaphore:
            uuid = await resolve_uuid(username)
            return username, uuid

    tasks = [_resolve_one(username) for username in usernames]
    completed = await asyncio.gather(*tasks, return_exceptions=True)

    for result in completed:
        if isinstance(result, Exception):
            log.error("hypixel.resolve.bulk.error", error=str(result))
            continue
        username, uuid = result
        results[username] = uuid

    return results


async def resolve_uuids_bulk(
    uuids: list[str],
) -> dict[str, str | None]:
    """Resolve multiple UUIDs to usernames in batch.

    Args:
        uuids: List of UUIDs to resolve.

    Returns:
        Dictionary mapping UUIDs to usernames (None for failed lookups).
    """
    log.info("hypixel.resolve.resolve_uuids_bulk", count=len(uuids))

    results: dict[str, str | None] = {}

    import asyncio

    semaphore = asyncio.Semaphore(10)

    async def _resolve_one(uuid: str) -> tuple[str, str | None]:
        async with semaphore:
            username = await resolve_username(uuid)
            return uuid, username

    tasks = [_resolve_one(uuid) for uuid in uuids]
    completed = await asyncio.gather(*tasks, return_exceptions=True)

    for result in completed:
        if isinstance(result, Exception):
            log.error("hypixel.resolve.bulk.error", error=str(result))
            continue
        uuid, username = result
        results[uuid] = username

    return results

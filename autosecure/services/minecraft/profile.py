"""Minecraft profile operations: UUID resolution, username lookup, profile data."""

from __future__ import annotations

import httpx
import structlog

from autosecure.utils.http import get_client

log = structlog.get_logger(__name__)

MC_SESSION_URL = "https://sessionserver.mojang.com/session/minecraft"
MC_API_URL = "https://api.mojang.com"


async def get_profile(ssid: str) -> dict | None:
    """Fetch Minecraft profile data using a Session ID.

    Args:
        ssid: Minecraft Session ID (access token from auth).

    Returns:
        Dictionary with profile data (name, uuid, skin_url) or None.
    """
    log.info("minecraft.profile.get_profile")

    try:
        async with get_client() as client:
            response = await client.get(
                f"{MC_SESSION_URL}/profile/{ssid}",
            )

            if response.status_code != 200:
                log.warning(
                    "minecraft.profile.get_profile.failed",
                    status=response.status_code,
                )
                return None

            data = response.json()
            uuid = data.get("id", "")
            name = data.get("name", "")
            skin_url = None

            for texture in data.get("properties", []):
                if texture.get("name") == "textures":
                    import base64
                    import json

                    try:
                        decoded = base64.b64decode(texture["value"])
                        textures = json.loads(decoded)
                        skin_data = textures.get("textures", {}).get("SKIN", {})
                        skin_url = skin_data.get("url")
                    except Exception:
                        pass

            return {
                "uuid": uuid,
                "name": name,
                "skin_url": skin_url,
                "raw": data,
            }

    except httpx.HTTPError as e:
        log.error("minecraft.profile.get_profile.http_error", error=str(e))
        return None
    except Exception as e:
        log.error("minecraft.profile.get_profile.error", error=str(e))
        return None


async def get_uuid(username: str) -> str | None:
    """Resolve a Minecraft username to UUID.

    Args:
        username: Minecraft username to resolve.

    Returns:
        UUID string without dashes, or None if not found.
    """
    log.info("minecraft.profile.get_uuid", username=username)

    try:
        async with get_client() as client:
            response = await client.get(
                f"{MC_API_URL}/users/profiles/minecraft/{username}",
            )

            if response.status_code != 200:
                log.warning(
                    "minecraft.profile.get_uuid.not_found",
                    username=username,
                )
                return None

            data = response.json()
            return data.get("id")

    except httpx.HTTPError as e:
        log.error("minecraft.profile.get_uuid.http_error", error=str(e))
        return None
    except Exception as e:
        log.error("minecraft.profile.get_uuid.error", error=str(e))
        return None


async def get_username(uuid: str) -> str | None:
    """Resolve a Minecraft UUID to username.

    Args:
        uuid: Minecraft UUID (with or without dashes).

    Returns:
        Current username, or None if not found.
    """
    clean_uuid = uuid.replace("-", "")
    log.info("minecraft.profile.get_username", uuid=clean_uuid)

    try:
        async with get_client() as client:
            response = await client.get(
                f"{MC_API_URL}/user/profiles/{clean_uuid}/names",
            )

            if response.status_code != 200:
                log.warning(
                    "minecraft.profile.get_username.not_found",
                    uuid=clean_uuid,
                )
                return None

            data = response.json()
            if not data:
                return None

            # Last entry is the current username
            return data[-1].get("name")

    except httpx.HTTPError as e:
        log.error("minecraft.profile.get_username.http_error", error=str(e))
        return None
    except Exception as e:
        log.error("minecraft.profile.get_username.error", error=str(e))
        return None

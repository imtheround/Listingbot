"""Minecraft skin and avatar operations."""

from __future__ import annotations

import httpx
import structlog

from autosecure.utils.http import get_client

log = structlog.get_logger(__name__)

MC_SESSION_URL = "https://sessionserver.mojang.com/session/minecraft"
MC_HEADS_URL = "https://mc-heads.net"
MC_VISAGE_URL = "https://visage.surgeplay.com"


async def get_skin(uuid: str) -> bytes | None:
    """Download a player's skin image.

    Args:
        uuid: Minecraft UUID (with or without dashes).

    Returns:
        Raw skin image bytes, or None on failure.
    """
    clean_uuid = uuid.replace("-", "")
    log.info("minecraft.skins.get_skin", uuid=clean_uuid)

    try:
        skin_url = f"{MC_HEADS_URL}/skin/{clean_uuid}"

        async with get_client() as client:
            response = await client.get(skin_url)

            if response.status_code != 200:
                log.warning(
                    "minecraft.skins.get_skin.failed",
                    status=response.status_code,
                )
                return None

            return response.content

    except httpx.HTTPError as e:
        log.error("minecraft.skins.get_skin.http_error", error=str(e))
        return None
    except Exception as e:
        log.error("minecraft.skins.get_skin.error", error=str(e))
        return None


def get_skin_url(uuid: str) -> str:
    """Get the full skin URL from mc-heads.net.

    Args:
        uuid: Minecraft UUID (with or without dashes).

    Returns:
        Full URL to the skin image.
    """
    clean_uuid = uuid.replace("-", "")
    return f"{MC_HEADS_URL}/skin/{clean_uuid}"


def get_avatar_url(uuid: str, size: int = 128) -> str:
    """Get a player's avatar/head URL.

    Args:
        uuid: Minecraft UUID (with or without dashes).
        size: Avatar size in pixels (default 128).

    Returns:
        URL to the player's head/avatar image.
    """
    clean_uuid = uuid.replace("-", "")
    return f"{MC_HEADS_URL}/{size}/{clean_uuid}"


def get_face_url(uuid: str, size: int = 128) -> str:
    """Get a player's face-only avatar URL.

    Args:
        uuid: Minecraft UUID (with or without dashes).
        size: Image size in pixels (default 128).

    Returns:
        URL to the player's face image.
    """
    clean_uuid = uuid.replace("-", "")
    return f"{MC_VISAGE_URL}/face/{size}/{clean_uuid}"


def get_bust_url(uuid: str, size: int = 128) -> str:
    """Get a player's bust (head + shoulders) URL.

    Args:
        uuid: Minecraft UUID (with or without dashes).
        size: Image size in pixels (default 128).

    Returns:
        URL to the player's bust image.
    """
    clean_uuid = uuid.replace("-", "")
    return f"{MC_VISAGE_URL}/bust/{size}/{clean_uuid}"

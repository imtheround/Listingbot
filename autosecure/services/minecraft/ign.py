"""Minecraft in-game name (IGN) change operations."""

from __future__ import annotations

import httpx
import structlog

from autosecure.utils.http import get_client

log = structlog.get_logger(__name__)

MC_API_URL = "https://api.mojang.com"
MC_SESSION_URL = "https://sessionserver.mojang.com/session/minecraft"

USERNAME_PATTERN = r"^[a-zA-Z0-9_]{3,16}$"


async def change_ign(ssid: str, new_name: str) -> bool:
    """Change the Minecraft in-game name for an authenticated account.

    Args:
        ssid: Minecraft Session ID (access token).
        new_name: Desired new username.

    Returns:
        True if the name change was successful, False otherwise.
    """
    if not validate_username(new_name):
        log.warning("minecraft.ign.change_ign.invalid_name", name=new_name)
        return False

    log.info("minecraft.ign.change_ign", new_name=new_name)

    try:
        async with get_client() as client:
            # Check if the name is available
            check_response = await client.get(
                f"{MC_API_URL}/user/profiles/minecraft/{new_name}/available",
            )

            if check_response.status_code != 200:
                log.warning(
                    "minecraft.ign.change_ign.check_failed",
                    status=check_response.status_code,
                )
                return False

            check_data = check_response.json()
            if not check_data.get("available", False):
                log.warning("minecraft.ign.change_ign.name_taken", name=new_name)
                return False

            # Perform the name change
            response = await client.put(
                f"{MC_SESSION_URL}/profile/name/{new_name}",
                headers={
                    "Authorization": f"Bearer {ssid}",
                    "Content-Type": "application/json",
                },
            )

            if response.status_code == 200:
                log.info("minecraft.ign.change_ign.success", new_name=new_name)
                return True

            log.warning(
                "minecraft.ign.change_ign.failed",
                status=response.status_code,
                body=response.text,
            )
            return False

    except httpx.HTTPError as e:
        log.error("minecraft.ign.change_ign.http_error", error=str(e))
        return False
    except Exception as e:
        log.error("minecraft.ign.change_ign.error", error=str(e))
        return False


def validate_username(username: str) -> bool:
    """Validate a Minecraft username format.

    Rules:
    - 3-16 characters long
    - Only alphanumeric characters and underscores
    - No consecutive underscores

    Args:
        username: Username to validate.

    Returns:
        True if the username is valid, False otherwise.
    """
    import re

    if not username or len(username) < 3 or len(username) > 16:
        return False

    if not re.match(USERNAME_PATTERN, username):
        return False

    # Check for consecutive underscores
    if "__" in username:
        return False

    # Check that it doesn't start or end with underscore
    return not (username.startswith("_") or username.endswith("_"))

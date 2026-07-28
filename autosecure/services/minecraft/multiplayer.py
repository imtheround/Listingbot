"""Xbox multiplayer privacy settings management."""

from __future__ import annotations

import structlog

from autosecure.utils.http import get_client

log = structlog.get_logger(__name__)

XBOX_PRIVACY_URL = "https://privacy.xboxlive.com/users/xuid({xuid})/settings"
XBOX_PROFILE_URL = "https://profile.xboxlive.com/users/xuid({xuid})/settings"
XBL_AUTH_URL = "https://user.auth.xboxlive.com/user/authenticate"
XSTS_AUTH_URL = "https://xsts.auth.xboxlive.com/xsts/authorize"
MC_LOGIN_URL = "https://api.minecraftservices.com/login_with_xbox"


async def enable_multiplayer(access_token: str) -> bool:
    """Enable Xbox multiplayer for a Minecraft account.

    Performs the full Xbox auth flow and updates privacy settings
    to allow multiplayer access.

    Args:
        access_token: Minecraft access token (from MSA auth).

    Returns:
        True if multiplayer was successfully enabled.
    """
    log.info("minecraft.multiplayer.enable_multiplayer")

    try:
        xuid = await _get_xuid_from_token(access_token)
        if not xuid:
            log.error("minecraft.multiplayer.enable_multiplayer.no_xuid")
            return False

        return await _update_privacy_setting(xuid, "multiplayer", "Allow", access_token)

    except Exception as e:
        log.error("minecraft.multiplayer.enable_multiplayer.error", error=str(e))
        return False


async def disable_multiplayer(access_token: str) -> bool:
    """Disable Xbox multiplayer for a Minecraft account.

    Args:
        access_token: Minecraft access token.

    Returns:
        True if multiplayer was successfully disabled.
    """
    log.info("minecraft.multiplayer.disable_multiplayer")

    try:
        xuid = await _get_xuid_from_token(access_token)
        if not xuid:
            return False

        return await _update_privacy_setting(xuid, "multiplayer", "Block", access_token)

    except Exception as e:
        log.error("minecraft.multiplayer.disable_multiplayer.error", error=str(e))
        return False


async def get_multiplayer_status(access_token: str) -> bool:
    """Check if multiplayer is currently enabled.

    Args:
        access_token: Minecraft access token.

    Returns:
        True if multiplayer is enabled, False if blocked or on error.
    """
    log.info("minecraft.multiplayer.get_multiplayer_status")

    try:
        xuid = await _get_xuid_from_token(access_token)
        if not xuid:
            return False

        async with get_client() as client:
            response = await client.get(
                XBOX_PRIVACY_URL.format(xuid=xuid),
                headers={
                    "Authorization": f"XBL3.0 x={access_token}",
                    "x-xbl-contract-version": "2",
                },
            )

            if response.status_code != 200:
                log.warning(
                    "minecraft.multiplayer.get_status.failed",
                    status=response.status_code,
                )
                return False

            data = response.json()
            settings_list = data.get("settings", [])

            for setting in settings_list:
                if setting.get("id") == "Multiplayer":
                    return setting.get("value") == "Allow"

            return False

    except Exception as e:
        log.error("minecraft.multiplayer.get_status.error", error=str(e))
        return False


async def _get_xuid_from_token(access_token: str) -> str | None:
    """Get XUID from a Minecraft access token via Xbox auth flow.

    Args:
        access_token: Minecraft access token.

    Returns:
        XUID string, or None on failure.
    """
    try:
        # Step 1: Exchange for XBL token
        async with get_client() as client:
            xbl_response = await client.post(
                XBL_AUTH_URL,
                json={
                    "Properties": {
                        "AuthMethod": "RPS",
                        "SiteName": "user.auth.xboxlive.com",
                        "RpsTicket": access_token,
                    },
                    "RelyingParty": "http://auth.xboxlive.com",
                    "TokenType": "JWT",
                },
                headers={"x-xbl-contract-version": "1"},
            )

            if xbl_response.status_code != 200:
                log.error(
                    "minecraft.multiplayer._get_xuid.xbl_failed",
                    status=xbl_response.status_code,
                )
                return None

            xbl_data = xbl_response.json()
            xbl_token = xbl_data.get("Token", "")

            # Step 2: Get XSTS token
            xsts_response = await client.post(
                XSTS_AUTH_URL,
                json={
                    "Properties": {
                        "SandboxId": "RETAIL",
                        "UserTokens": [xbl_token],
                    },
                    "RelyingParty": "rp://api.minecraftservices.com/",
                    "TokenType": "JWT",
                },
                headers={"x-xbl-contract-version": "2"},
            )

            if xsts_response.status_code != 200:
                log.error(
                    "minecraft.multiplayer._get_xuid.xsts_failed",
                    status=xsts_response.status_code,
                )
                return None

            xsts_data = xsts_response.json()
            xsts_token = xsts_data.get("Token", "")

            # Step 3: Get MC token and extract XUID
            mc_response = await client.post(
                MC_LOGIN_URL,
                json={"identityToken": f"XBL3.0 x={xsts_token}"},
            )

            if mc_response.status_code != 200:
                return None

            # Extract XUID from the XBL claims
            for claim in xbl_data.get("DisplayClaims", {}).get("xui", []):
                if "xid" in claim:
                    return claim["xid"]

            return None

    except Exception as e:
        log.error("minecraft.multiplayer._get_xuid.error", error=str(e))
        return None


async def _update_privacy_setting(
    xuid: str,
    setting_name: str,
    value: str,
    access_token: str,
) -> bool:
    """Update an Xbox privacy setting.

    Args:
        xuid: Xbox User ID.
        setting_name: Privacy setting name (e.g., "multiplayer").
        value: Setting value (e.g., "Allow", "Block").
        access_token: Authentication token.

    Returns:
        True if the setting was updated successfully.
    """
    try:
        async with get_client() as client:
            response = await client.post(
                XBOX_PRIVACY_URL.format(xuid=xuid),
                json={
                    "settings": [
                        {
                            "id": setting_name.capitalize(),
                            "value": value,
                        }
                    ]
                },
                headers={
                    "Authorization": f"XBL3.0 x={access_token}",
                    "x-xbl-contract-version": "2",
                    "Content-Type": "application/json",
                },
            )

            if response.status_code in (200, 204):
                log.info(
                    "minecraft.multiplayer._update_setting.success",
                    setting=setting_name,
                    value=value,
                )
                return True

            log.warning(
                "minecraft.multiplayer._update_setting.failed",
                status=response.status_code,
                body=response.text,
            )
            return False

    except Exception as e:
        log.error("minecraft.multiplayer._update_setting.error", error=str(e))
        return False

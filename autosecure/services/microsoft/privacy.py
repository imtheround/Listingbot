"""Microsoft/Xbox privacy and multiplayer settings."""

from __future__ import annotations

import structlog

from autosecure.services.microsoft._http import MicrosoftHTTPClient

log = structlog.get_logger("microsoft.privacy")

PRIVACY_API = "https://privacy.xboxlive.com"
XBOXLIVE_SETTINGS_API = "https://settings.xboxlive.com"


class MicrosoftPrivacy:
    """Manages Xbox privacy and multiplayer settings.

    Provides methods to query and modify the Xbox multiplayer status.
    """

    def __init__(self, proxy: str | None = None) -> None:
        """Initialize the privacy manager.

        Args:
            proxy: Optional proxy URL for requests.
        """
        self.proxy = proxy

    def _auth_headers(self, access_token: str) -> dict[str, str]:
        """Build authorization headers for Xbox privacy APIs.

        Args:
            access_token: The Xbox Live access token.

        Returns:
            Headers dict.
        """
        return {
            "Authorization": f"XBL3.0 x={access_token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    async def get_multiplayer_status(self, access_token: str) -> bool:
        """Check if Xbox multiplayer is enabled on the account.

        Args:
            access_token: The Xbox Live access token.

        Returns:
            True if multiplayer is enabled, False otherwise.
        """
        headers = self._auth_headers(access_token)
        async with MicrosoftHTTPClient(proxy=self.proxy) as client:
            try:
                response = await client.get(
                    f"{PRIVACY_API}/users/me/settings/multiplayer",
                    headers=headers,
                )
                data = response.json()
                # The setting value can vary; typically "Allow" means enabled
                setting = data.get("setting", data.get("value", ""))
                enabled = setting in ("Allow", "allow", "Everyone", True)
                log.info("multiplayer_status", enabled=enabled)
                return enabled
            except Exception as exc:
                log.error("multiplayer_status_failed", error=str(exc))
                return False

    async def set_multiplayer(self, access_token: str, enabled: bool) -> bool:
        """Enable or disable Xbox multiplayer.

        Args:
            access_token: The Xbox Live access token.
            enabled: True to enable multiplayer, False to disable.

        Returns:
            True if the setting was updated successfully.
        """
        headers = self._auth_headers(access_token)
        value = "Allow" if enabled else "Block"
        async with MicrosoftHTTPClient(proxy=self.proxy) as client:
            try:
                response = await client.put(
                    f"{PRIVACY_API}/users/me/settings/multiplayer",
                    json={"setting": value},
                    headers=headers,
                )
                success = response.status_code in (200, 204)
                log.info("multiplayer_set", enabled=enabled, success=success)
                return success
            except Exception as exc:
                log.error("multiplayer_set_failed", error=str(exc))
                return False

"""Microsoft OAuth consent management."""

from __future__ import annotations

import structlog

from autosecure.services.microsoft._http import MicrosoftHTTPClient

log = structlog.get_logger("microsoft.oauth")

CONSENT_API = "https://account.live.com/consent/Manage"


class MicrosoftOAuth:
    """Manages OAuth application consents on a Microsoft account.

    Provides methods to list, revoke, and bulk-revoke OAuth consents.
    """

    def __init__(self, proxy: str | None = None) -> None:
        """Initialize the OAuth manager.

        Args:
            proxy: Optional proxy URL for requests.
        """
        self.proxy = proxy

    def _auth_headers(self, access_token: str) -> dict[str, str]:
        """Build authorization headers for OAuth APIs.

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

    async def get_consents(self, access_token: str) -> list[dict]:
        """List all OAuth application consents on the account.

        Args:
            access_token: The Xbox Live access token.

        Returns:
            A list of consent dictionaries with client_id, app_name, etc.
        """
        headers = self._auth_headers(access_token)
        async with MicrosoftHTTPClient(proxy=self.proxy) as client:
            try:
                response = await client.get(
                    CONSENT_API,
                    headers=headers,
                )
                data = response.json()
                consents = data.get("consents", data.get("Consents", []))
                log.info("consents_fetched", count=len(consents))
                return consents
            except Exception as exc:
                log.error("consents_fetch_failed", error=str(exc))
                return []

    async def remove_consent(self, access_token: str, client_id: str) -> bool:
        """Remove a single OAuth consent by client ID.

        Args:
            access_token: The Xbox Live access token.
            client_id: The OAuth application client ID.

        Returns:
            True if the consent was removed successfully.
        """
        headers = self._auth_headers(access_token)
        async with MicrosoftHTTPClient(proxy=self.proxy) as client:
            try:
                response = await client.post(
                    f"{CONSENT_API}/Revoke",
                    json={"client_id": client_id},
                    headers=headers,
                )
                log.info("consent_removed", client_id=client_id, status=response.status_code)
                return response.status_code in (200, 204)
            except Exception as exc:
                log.error("consent_remove_failed", client_id=client_id, error=str(exc))
                return False

    async def remove_all_consents(self, access_token: str) -> int:
        """Remove all OAuth consents from the account.

        Args:
            access_token: The Xbox Live access token.

        Returns:
            The number of consents successfully removed.
        """
        consents = await self.get_consents(access_token)
        if not consents:
            return 0

        removed = 0
        for consent in consents:
            client_id = consent.get("client_id") or consent.get("ClientId", "")
            if client_id:
                success = await self.remove_consent(access_token, client_id)
                if success:
                    removed += 1

        log.info("all_consents_removed", removed=removed, total=len(consents))
        return removed

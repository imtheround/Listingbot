"""Microsoft two-factor authentication status and proofs."""

from __future__ import annotations

import structlog

from autosecure.services.microsoft._http import MicrosoftHTTPClient

log = structlog.get_logger("microsoft.tfa")

TFA_API = "https://account.live.com/proofs"


class MicrosoftTFA:
    """Manages two-factor authentication information for Microsoft accounts.

    Provides methods to check TFA status and list registered proofs.
    """

    def __init__(self, proxy: str | None = None) -> None:
        """Initialize the TFA manager.

        Args:
            proxy: Optional proxy URL for requests.
        """
        self.proxy = proxy

    def _auth_headers(self, access_token: str) -> dict[str, str]:
        """Build authorization headers for TFA APIs.

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

    async def check_tfa_status(self, access_token: str) -> bool:
        """Check if two-factor authentication is enabled on the account.

        Args:
            access_token: The Xbox Live access token.

        Returns:
            True if TFA is enabled, False otherwise.
        """
        async with MicrosoftHTTPClient(proxy=self.proxy) as client:
            try:
                response = await client.get(
                    f"{TFA_API}/Manager",
                    headers=self._auth_headers(access_token),
                )
                data = response.json()
                enabled = data.get("IsTwoFactorEnabled", False)
                log.info("tfa_status", enabled=enabled)
                return enabled
            except Exception as exc:
                log.error("tfa_status_failed", error=str(exc))
                return False

    async def get_tfa_proofs(self, access_token: str) -> list[dict]:
        """Retrieve all registered two-factor authentication proofs.

        Args:
            access_token: The Xbox Live access token.

        Returns:
            A list of proof dictionaries (phone, email, authenticator, etc.).
        """
        async with MicrosoftHTTPClient(proxy=self.proxy) as client:
            try:
                response = await client.get(
                    f"{TFA_API}/Authenticators",
                    headers=self._auth_headers(access_token),
                )
                data = response.json()
                proofs = data.get("proofs", data.get("Proofs", []))
                log.info("tfa_proofs_fetched", count=len(proofs))
                return proofs
            except Exception as exc:
                log.error("tfa_proofs_fetch_failed", error=str(exc))
                return []

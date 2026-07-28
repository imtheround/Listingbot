"""Microsoft Family Group operations."""

from __future__ import annotations

import structlog

from autosecure.services.microsoft._http import MicrosoftHTTPClient

log = structlog.get_logger("microsoft.family")

FAMILY_API = "https://family.microsoft.com"


class MicrosoftFamily:
    """Manages Microsoft Family Group membership.

    Provides methods to list family members, retrieve the PUID,
    and leave a family group.
    """

    def __init__(self, proxy: str | None = None) -> None:
        """Initialize the family manager.

        Args:
            proxy: Optional proxy URL for requests.
        """
        self.proxy = proxy

    def _auth_headers(self, access_token: str) -> dict[str, str]:
        """Build authorization headers for family APIs.

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

    async def get_family_members(self, access_token: str) -> list[dict]:
        """Retrieve all members of the Microsoft Family Group.

        Args:
            access_token: The Xbox Live access token.

        Returns:
            A list of family member dictionaries.
        """
        headers = self._auth_headers(access_token)
        async with MicrosoftHTTPClient(proxy=self.proxy) as client:
            try:
                response = await client.get(
                    f"{FAMILY_API}/api/v1/family/members",
                    headers=headers,
                )
                data = response.json()
                members = data.get("members", data.get("Members", []))
                log.info("family_members_fetched", count=len(members))
                return members
            except Exception as exc:
                log.error("family_members_fetch_failed", error=str(exc))
                return []

    async def get_puid(self, access_token: str) -> str | None:
        """Retrieve the account's PUID (Personal User ID).

        Args:
            access_token: The Xbox Live access token.

        Returns:
            The PUID string, or None if retrieval fails.
        """
        headers = self._auth_headers(access_token)
        async with MicrosoftHTTPClient(proxy=self.proxy) as client:
            try:
                response = await client.get(
                    "https://user.auth.xboxlive.com/user/authenticate",
                    headers=headers,
                )
                data = response.json()
                puid = data.get("IssueInstant", None)
                # The PUID is in the Authorization header or profile response
                profile_resp = await client.get(
                    "https://profile.xboxlive.com/users/me",
                    headers=self._auth_headers(access_token),
                )
                profile_data = profile_resp.json()
                puid = profile_data.get("id") or profile_data.get("xuid")
                log.info("puid_fetched", puid=puid[:8] if puid else None)
                return puid
            except Exception as exc:
                log.error("puid_fetch_failed", error=str(exc))
                return None

    async def leave_family(self, access_token: str) -> bool:
        """Leave the Microsoft Family Group.

        Args:
            access_token: The Xbox Live access token.

        Returns:
            True if the account successfully left the family group.
        """
        headers = self._auth_headers(access_token)
        async with MicrosoftHTTPClient(proxy=self.proxy) as client:
            try:
                puid = await self.get_puid(access_token)
                if not puid:
                    log.error("leave_family_no_puid")
                    return False

                response = await client.post(
                    f"{FAMILY_API}/api/v1/family/members/{puid}/remove",
                    headers=headers,
                )
                success = response.status_code in (200, 204)
                log.info("leave_family_result", success=success)
                return success
            except Exception as exc:
                log.error("leave_family_failed", error=str(exc))
                return False

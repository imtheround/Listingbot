"""Microsoft account profile management operations."""

from __future__ import annotations

import structlog

from autosecure.services.microsoft._http import MicrosoftHTTPClient

log = structlog.get_logger("microsoft.profile")

PROFILE_API = "https://profile.xboxlive.com"
ACCOUNT_API = "https://account.xbox.com"
ACCOUNT_MS_API = "https://account.microsoft.com"


class MicrosoftProfile:
    """Manages Microsoft/Xbox profile modifications.

    Handles name, date of birth, profile picture, and language changes
    with CSRF token extraction and captcha handling.
    """

    def __init__(self, proxy: str | None = None) -> None:
        """Initialize the profile manager.

        Args:
            proxy: Optional proxy URL for requests.
        """
        self.proxy = proxy

    def _auth_headers(self, access_token: str) -> dict[str, str]:
        """Build authorization headers for Xbox Live APIs.

        Args:
            access_token: The Xbox Live access token.

        Returns:
            Headers dict with Authorization and content type.
        """
        return {
            "Authorization": f"XBL3.0 x={access_token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    async def _get_csrf_token(self, access_token: str) -> tuple[str, str]:
        """Extract a CSRF token from the Xbox profile page.

        Args:
            access_token: The Xbox Live access token.

        Returns:
            A tuple of (csrf_token, cookies_string).
        """
        async with MicrosoftHTTPClient(proxy=self.proxy) as client:
            response = await client.get(
                f"{ACCOUNT_MS_API}/profile",
                headers=self._auth_headers(access_token),
            )
            html = response.text

            import re

            token_match = re.search(
                r'<meta[^>]+name="csrf-token"[^>]+content="([^"]+)"', html
            )
            token = token_match.group(1) if token_match else ""
            return token, "; ".join(f"{k}={v}" for k, v in client.cookies.items())

    async def change_name(
        self, access_token: str, first_name: str, last_name: str
    ) -> bool:
        """Change the account display name.

        Args:
            access_token: The Xbox Live access token.
            first_name: New first name.
            last_name: New last name.

        Returns:
            True if the name was changed successfully.
        """
        headers = self._auth_headers(access_token)
        async with MicrosoftHTTPClient(proxy=self.proxy) as client:
            csrf_token, _ = await self._get_csrf_token(access_token)
            headers["x-csrf-token"] = csrf_token

            payload = {
                "firstName": first_name,
                "lastName": last_name,
            }

            try:
                response = await client.put(
                    f"{PROFILE_API}/users/me/profile/settings/gamertag",
                    json=payload,
                    headers=headers,
                )
                log.info("name_changed", status=response.status_code)
                return response.status_code == 200
            except Exception as exc:
                log.error("name_change_failed", error=str(exc))
                return False

    async def change_dob(
        self,
        access_token: str,
        day: int,
        month: int,
        year: int,
        country: str = "US",
    ) -> bool:
        """Change the account date of birth.

        Args:
            access_token: The Xbox Live access token.
            day: Day of birth (1-31).
            month: Month of birth (1-12).
            year: Year of birth.
            country: Two-letter country code.

        Returns:
            True if the DOB was changed successfully.
        """
        headers = self._auth_headers(access_token)
        async with MicrosoftHTTPClient(proxy=self.proxy) as client:
            csrf_token, _ = await self._get_csrf_token(access_token)
            headers["x-csrf-token"] = csrf_token

            payload = {
                "birthDate": f"{year:04d}-{month:02d}-{day:02d}",
                "country": country,
            }

            try:
                response = await client.put(
                    f"{PROFILE_API}/users/me/profile/settings",
                    json=payload,
                    headers=headers,
                )
                log.info("dob_changed", status=response.status_code)
                return response.status_code == 200
            except Exception as exc:
                log.error("dob_change_failed", error=str(exc))
                return False

    async def change_pfp(self, access_token: str, image_bytes: bytes) -> bool:
        """Change the account profile picture.

        Args:
            access_token: The Xbox Live access token.
            image_bytes: Raw image data (PNG/JPG).

        Returns:
            True if the PFP was changed successfully.
        """
        headers = self._auth_headers(access_token)
        headers["Content-Type"] = "image/png"
        async with MicrosoftHTTPClient(proxy=self.proxy) as client:
            try:
                response = await client.put(
                    f"{PROFILE_API}/users/me/profile/settings/picture",
                    content=image_bytes,
                    headers=headers,
                )
                log.info("pfp_changed", status=response.status_code)
                return response.status_code == 200
            except Exception as exc:
                log.error("pfp_change_failed", error=str(exc))
                return False

    async def change_language(self, access_token: str, locale: str) -> bool:
        """Change the account display language.

        Args:
            access_token: The Xbox Live access token.
            locale: BCP 47 language tag (e.g. "en-US", "fr-FR").

        Returns:
            True if the language was changed successfully.
        """
        headers = self._auth_headers(access_token)
        async with MicrosoftHTTPClient(proxy=self.proxy) as client:
            csrf_token, _ = await self._get_csrf_token(access_token)
            headers["x-csrf-token"] = csrf_token

            payload = {
                "locale": locale,
            }

            try:
                response = await client.put(
                    f"{PROFILE_API}/users/me/profile/settings",
                    json=payload,
                    headers=headers,
                )
                log.info("language_changed", status=response.status_code)
                return response.status_code == 200
            except Exception as exc:
                log.error("language_change_failed", error=str(exc))
                return False

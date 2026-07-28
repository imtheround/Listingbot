"""Microsoft session state checking and token refresh."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import structlog

from autosecure.services.microsoft._http import MicrosoftHTTPClient

log = structlog.get_logger("microsoft.session")

TOKEN_URL = "https://login.live.com/oauth20_token.srf"
XBOX_TOKEN_URL = "https://user.auth.xboxlive.com/user/authenticate"


@dataclass
class SessionState:
    """Represents the current state of a Microsoft session."""

    valid: bool
    access_token: str | None = None
    expires_in: int | None = None
    error: str | None = None


class MicrosoftSession:
    """Manages Microsoft session validation and token refresh.

    Provides methods to check session validity and refresh tokens.
    """

    def __init__(self, proxy: str | None = None) -> None:
        """Initialize the session manager.

        Args:
            proxy: Optional proxy URL for requests.
        """
        self.proxy = proxy

    async def check_session_state(self, access_token: str) -> SessionState:
        """Check if the current session is still valid.

        Args:
            access_token: The Xbox Live access token to validate.

        Returns:
            SessionState indicating whether the session is valid.
        """
        async with MicrosoftHTTPClient(proxy=self.proxy) as client:
            try:
                response = await client.get(
                    "https://profile.xboxlive.com/users/me",
                    headers={
                        "Authorization": f"XBL3.0 x={access_token}",
                        "Accept": "application/json",
                    },
                )
                if response.status_code == 200:
                    log.info("session_valid")
                    return SessionState(valid=True, access_token=access_token)
                log.warning("session_invalid", status=response.status_code)
                return SessionState(
                    valid=False,
                    error=f"Session returned status {response.status_code}",
                )
            except Exception as exc:
                log.error("session_check_failed", error=str(exc))
                return SessionState(valid=False, error=str(exc))

    async def refresh_token(self, refresh_token: str) -> dict[str, Any]:
        """Refresh an OAuth token using a refresh token.

        Args:
            refresh_token: The refresh token to use.

        Returns:
            A dict with new access_token, refresh_token, and expires_in,
            or an error key on failure.
        """
        async with MicrosoftHTTPClient(proxy=self.proxy) as client:
            try:
                response = await client.post(
                    TOKEN_URL,
                    data={
                        "client_id": "000000004C124E29",
                        "grant_type": "refresh_token",
                        "scope": "service::user.auth.xboxlive.com::MBI_SSL",
                        "refresh_token": refresh_token,
                    },
                    headers={
                        "Content-Type": "application/x-www-form-urlencoded",
                    },
                )
                data = response.json()
                if "access_token" in data:
                    log.info("token_refreshed")
                    return {
                        "access_token": data["access_token"],
                        "refresh_token": data.get("refresh_token", refresh_token),
                        "expires_in": data.get("expires_in", 3600),
                    }
                error = data.get("error_description", data.get("error", "Unknown error"))
                log.warning("token_refresh_failed", error=error)
                return {"error": error}
            except Exception as exc:
                log.error("token_refresh_exception", error=str(exc))
                return {"error": str(exc)}

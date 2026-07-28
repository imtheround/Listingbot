"""Xbox Live / XSTS authentication for Minecraft accounts."""

from __future__ import annotations

from dataclasses import dataclass

import httpx
import structlog

from autosecure.core.config import settings
from autosecure.utils.http import get_client

log = structlog.get_logger(__name__)

XBL_AUTH_URL = "https://user.auth.xboxlive.com/user/authenticate"
XBL_LOGIN_URL = "https://login.live.com/ppsecure/post.srf"
XSTS_AUTH_URL = "https://xsts.auth.xboxlive.com/xsts/authorize"
MC_LOGIN_URL = "https://api.minecraftservices.com/login_with_xbox"
MC_AUTH_HEADER = "XBL3.0 x={userHash};{dToken}"


@dataclass
class MCAuthResult:
    """Result of a Minecraft authentication attempt."""

    success: bool
    xbl_token: str = ""
    xsts_token: str = ""
    user_hash: str = ""
    ssid: str = ""
    error: str = ""
    access_token: str = ""


async def xbl_login(email: str, password: str) -> MCAuthResult:
    """Authenticate with Xbox Live using Microsoft account credentials.

    Performs the full Microsoft account login flow to obtain an Xbox Live token.

    Args:
        email: Microsoft account email address.
        password: Microsoft account password.

    Returns:
        MCAuthResult containing the XBL token or error details.
    """
    log.info("minecraft.auth.xbl_login", email=email)

    try:
        async with get_client() as client:
            # Step 1: Get Microsoft login page to extract flow tokens
            login_page = await client.get(
                "https://login.live.com/",
                params={
                    "wa": "wsignin1.0",
                    "wreply": settings.microsoft.redirect_uri,
                    "id": "292841",
                    "cobrandid": "90015",
                },
            )

            # Extract SFT, SU, PPFT from the login page
            sft = _extract_input_value(login_page.text, "sFTTag")
            context = _extract_input_value(login_page.text, "uaid")

            if not sft:
                return MCAuthResult(success=False, error="Failed to extract login tokens")

            # Step 2: Submit credentials
            auth_response = await client.post(
                settings.microsoft.auth_url,
                data={
                    "login": email,
                    "loginfmt": email,
                    "passwd": password,
                    "uaid": context,
                    "SFT": sft,
                    "SFTTag": sft,
                    "PPFT": sft,
                    "PPSX": "Passport",
                    "psi": "xblsignin",
                    "idsbtk": "1",
                    "SpawnRedir": "true",
                    "NewUser": "1",
                    "uiflvr": "1008",
                    "hpgrequestid": context,
                    "FlowToken": sft,
                    "cobrandid": "90015",
                    "i12": "1",
                    "cookieproof": "1",
                    "lc": "1033",
                    "sdkVersion": "1.0.0",
                },
                headers={
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Cookie": f"ESTSAUTHPERSISTENT=; ESTSAUTHLIGHT=; MicrosoftAccountConfigured=; ANON=; __Host-MSAccountsRP=; RPSSecAuth=; RRW=; SC=; uaid={context}",
                },
                follow_redirects=True,
            )

            if auth_response.status_code != 200:
                error_msg = _extract_error(auth_response.text)
                return MCAuthResult(success=False, error=f"Login failed: {error_msg}")

            # Check for 2FA requirement
            if "TwoFactor" in auth_response.url or "Suspended" in auth_response.url:
                return MCAuthResult(success=False, error="Two-factor authentication required")

            # Extract XBL token from redirect
            xbl_token = _extract_token_from_redirect(auth_response)
            if not xbl_token:
                xbl_token = _extract_input_value(auth_response.text, "t")

            if not xbl_token:
                return MCAuthResult(success=False, error="Failed to extract XBL token")

            # Step 3: Get XBL user token
            xbl_user_response = await client.post(
                XBL_AUTH_URL,
                json={
                    "Properties": {
                        "AuthMethod": "RPS",
                        "SiteName": "user.auth.xboxlive.com",
                        "RpsTicket": xbl_token,
                    },
                    "RelyingParty": "http://auth.xboxlive.com",
                    "TokenType": "JWT",
                },
                headers={"x-xbl-contract-version": "1"},
            )

            if xbl_user_response.status_code != 200:
                return MCAuthResult(success=False, error="Failed to get XBL user token")

            xbl_data = xbl_user_response.json()
            xbl_user_token = xbl_data.get("Token", "")
            user_hash = _extract_user_hash(xbl_data)

            if not xbl_user_token:
                return MCAuthResult(success=False, error="Empty XBL user token")

            return MCAuthResult(
                success=True,
                xbl_token=xbl_user_token,
                user_hash=user_hash,
            )

    except httpx.HTTPError as e:
        log.error("minecraft.auth.xbl_login.http_error", error=str(e))
        return MCAuthResult(success=False, error=f"HTTP error: {e}")
    except Exception as e:
        log.error("minecraft.auth.xbl_login.error", error=str(e))
        return MCAuthResult(success=False, error=str(e))


async def get_xsts_token(xbl_token: str) -> MCAuthResult:
    """Authorize an XBL token with XSTS for Minecraft access.

    Args:
        xbl_token: Xbox Live user token.

    Returns:
        MCAuthResult containing the XSTS token or error details.
    """
    log.info("minecraft.auth.get_xsts_token")

    try:
        async with get_client() as client:
            response = await client.post(
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

            if response.status_code != 200:
                data = response.json()
                error_msg = data.get("XErr", "Unknown XSTS error")
                return MCAuthResult(
                    success=False,
                    error=f"XSTS authorization failed: {error_msg}",
                )

            data = response.json()
            xsts_token = data.get("Token", "")
            if not xsts_token:
                return MCAuthResult(success=False, error="Empty XSTS token")

            return MCAuthResult(success=True, xsts_token=xsts_token)

    except httpx.HTTPError as e:
        log.error("minecraft.auth.get_xsts_token.http_error", error=str(e))
        return MCAuthResult(success=False, error=f"HTTP error: {e}")
    except Exception as e:
        log.error("minecraft.auth.get_xsts_token.error", error=str(e))
        return MCAuthResult(success=False, error=str(e))


async def get_ssid(xsts_token: str) -> str:
    """Exchange XSTS token for Minecraft Session ID (SSID).

    Args:
        xsts_token: Xbox XSTS authorization token.

    Returns:
        The Minecraft Session ID string, or empty string on failure.
    """
    log.info("minecraft.auth.get_ssid")

    try:
        async with get_client() as client:
            response = await client.post(
                MC_LOGIN_URL,
                json={"identityToken": f"XBL3.0 x={xsts_token}"},
            )

            if response.status_code != 200:
                log.error(
                    "minecraft.auth.get_ssid.failed",
                    status=response.status_code,
                    body=response.text,
                )
                return ""

            data = response.json()
            ssid = data.get("access_token", "")
            if not ssid:
                log.error("minecraft.auth.get_ssid.no_token", data=data)
            return ssid

    except httpx.HTTPError as e:
        log.error("minecraft.auth.get_ssid.http_error", error=str(e))
        return ""
    except Exception as e:
        log.error("minecraft.auth.get_ssid.error", error=str(e))
        return ""


def _extract_input_value(html: str, name: str) -> str:
    """Extract a hidden input value from HTML."""
    import re

    pattern = rf'name="{name}"[^>]*value="([^"]*)"'
    match = re.search(pattern, html)
    return match.group(1) if match else ""


def _extract_error(html: str) -> str:
    """Extract error message from Microsoft login page."""
    import re

    patterns = [
        r'<p[^>]*id="errorMsg"[^>]*>(.*?)</p>',
        r'class="error"[^>]*>(.*?)<',
        r'<strong[^>]*>(.*?)</strong>',
    ]
    for pattern in patterns:
        match = re.search(pattern, html, re.DOTALL)
        if match:
            return match.group(1).strip()
    return "Unknown login error"


def _extract_token_from_redirect(response: httpx.Response) -> str:
    """Extract XBL token from redirect chain."""
    import re

    for history_response in response.history:
        match = re.search(r"access_token=([^&]+)", str(history_response.headers))
        if match:
            return match.group(1)

    match = re.search(r"access_token=([^&]+)", str(response.url))
    if match:
        return match.group(1)
    return ""


def _extract_user_hash(xbl_data: dict) -> str:
    """Extract user hash from XBL auth response."""
    try:
        for claim in xbl_data.get("DisplayClaims", {}).get("xui", []):
            if "ush" in claim:
                return claim["ush"]
    except (KeyError, TypeError):
        pass
    return ""

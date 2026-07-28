"""Microsoft account authentication flows."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import TYPE_CHECKING

import structlog

from autosecure.core.exceptions import (
    AccountLocked,
    CaptchaRequired,
    InvalidCredentials,
)
from autosecure.services.microsoft._http import MicrosoftHTTPClient

if TYPE_CHECKING:
    import httpx

log = structlog.get_logger("microsoft.auth")

LOGIN_URL = "https://login.live.com/ppsecure/post.srf"
LOGIN_PAGE_URL = "https://login.live.com/"
XBOX_XSTS_URL = "https://xsts.auth.xboxlive.com/xsts/authorize"
XBOX_LOGIN_URL = "https://user.auth.xboxlive.com/user/authenticate"
MC_PROFILE_URL = "https://api.minecraftservices.com/minecraft/profile"
MC_AUTH_URL = "https://api.minecraftservices.com/authentication/login_with_xbox"
MSA_AUTH_URL = "https://login.live.com/oauth20_token.srf"


@dataclass
class MSAuthResult:
    """Result of a Microsoft authentication attempt."""

    success: bool
    cookies: dict[str, str] | None = None
    access_token: str | None = None
    refresh_token: str | None = None
    expires_in: int | None = None
    error: str | None = None
    error_code: str | None = None


@dataclass
class LoginData:
    """PPFT token and cookies required to initiate a login flow."""

    ppft: str
    cookies: dict[str, str]
    url_post: str
    url_event: str
    sFTTag: str


class MicrosoftAuth:
    """Handles all Microsoft account login flows.

    Provides methods for OTP, password, recovery code, MSAUTH cookie,
    and security link authentication.
    """

    def __init__(self, proxy: str | None = None) -> None:
        """Initialize the auth handler.

        Args:
            proxy: Optional proxy URL for requests.
        """
        self.proxy = proxy

    async def get_login_data(self) -> LoginData:
        """Fetch the PPFT token and cookies from login.live.com.

        Returns:
            LoginData containing the PPFT token, cookies, and form URLs.

        Raises:
            InvalidCredentials: If the login page cannot be loaded.
        """
        async with MicrosoftHTTPClient(proxy=self.proxy) as client:
            response = await client.get(LOGIN_PAGE_URL)
            html = response.text

            ppft_match = re.search(r'<input[^>]+name="PPFT"[^>]+value="([^"]+)"', html)
            if not ppft_match:
                log.error("ppft_not_found")
                raise InvalidCredentials("Could not extract PPFT token from login page")
            ppft = ppft_match.group(1)

            url_post_match = re.search(r'<form[^>]+id="f"[^>]+action="([^"]+)"', html)
            url_post = url_post_match.group(1) if url_post_match else LOGIN_URL
            url_post = url_post.replace("&amp;", "&")

            url_event_match = re.search(r'<script[^>]+>\s*var\s+fCanary\s*=\s*\{[^}]*"url"\s*:\s*"([^"]+)"', html)
            url_event = url_event_match.group(1) if url_event_match else ""

            sft_match = re.search(r'<input[^>]+name="uaid"[^>]+value="([^"]+)"', html)
            sFTTag = sft_match.group(1) if sft_match else ""

            cookies = dict(client.cookies)

            log.info("login_data_fetched")
            return LoginData(
                ppft=ppft,
                cookies=cookies,
                url_post=url_post,
                url_event=url_event,
                sFTTag=sFTTag,
            )

    async def login_with_otp(
        self, email: str, otp: str, password: str | None = None
    ) -> MSAuthResult:
        """Login using a one-time password / verification code.

        Args:
            email: The Microsoft account email address.
            otp: The one-time password / verification code.
            password: Optional password if required alongside OTP.

        Returns:
            MSAuthResult with cookies and access token on success.
        """
        login_data = await self.get_login_data()
        async with MicrosoftHTTPClient(
            proxy=self.proxy, cookies=login_data.cookies
        ) as client:
            payload = {
                "login": email,
                "loginFmt": email,
                "i13": "0",
                "mam": "0",
                "m1": "0",
                "loginSrc": "0",
                "uaid": login_data.sFTTag,
                "ppFTT": login_data.ppft,
                "sFTTag": login_data.sFTTag,
                "hpgrequestid": login_data.sFTTag,
                "psRetsCipherLength": "0",
                "encryptedPostData": "",
            }

            if password:
                payload["passwd"] = password
            else:
                payload["otc"] = otp

            response = await client.post(
                login_data.url_post,
                data=payload,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )

            return self._parse_login_response(response, dict(client.cookies))

    async def login_with_password(
        self, email: str, password: str
    ) -> MSAuthResult:
        """Login using email and password.

        Args:
            email: The Microsoft account email address.
            password: The account password.

        Returns:
            MSAuthResult with cookies and access token on success.
        """
        login_data = await self.get_login_data()
        async with MicrosoftHTTPClient(
            proxy=self.proxy, cookies=login_data.cookies
        ) as client:
            payload = {
                "login": email,
                "loginFmt": email,
                "i13": "0",
                "passwd": password,
                "psRetsCipherLength": "0",
                "encryptedPostData": "",
                "uaid": login_data.sFTTag,
                "ppFTT": login_data.ppft,
                "sFTTag": login_data.sFTTag,
                "hpgrequestid": login_data.sFTTag,
            }

            response = await client.post(
                login_data.url_post,
                data=payload,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )

            return self._parse_login_response(response, dict(client.cookies))

    async def login_with_recovery_code(
        self, email: str, recovery_code: str
    ) -> MSAuthResult:
        """Login using an account recovery code.

        Args:
            email: The Microsoft account email address.
            recovery_code: The account recovery code.

        Returns:
            MSAuthResult with cookies and access token on success.
        """
        login_data = await self.get_login_data()
        async with MicrosoftHTTPClient(
            proxy=self.proxy, cookies=login_data.cookies
        ) as client:
            payload = {
                "login": email,
                "loginFmt": email,
                "i13": "0",
                "t": recovery_code,
                "type": "29",
                "psRetsCipherLength": "0",
                "encryptedPostData": "",
                "uaid": login_data.sFTTag,
                "ppFTT": login_data.ppft,
                "sFTTag": login_data.sFTTag,
                "hpgrequestid": login_data.sFTTag,
            }

            response = await client.post(
                login_data.url_post,
                data=payload,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )

            return self._parse_login_response(response, dict(client.cookies))

    async def login_with_msauth(self, msauth_cookie: str) -> MSAuthResult:
        """Login using an MSAUTH cookie value.

        Args:
            msauth_cookie: The MSAUTH cookie string.

        Returns:
            MSAuthResult with cookies and access token on success.
        """
        async with MicrosoftHTTPClient(proxy=self.proxy) as client:
            client.set_cookies({"MSAUTH": msauth_cookie})
            await client.get(
                "https://www.xbox.com/en-US/auth/msa/blank.html",
            )

            all_cookies = dict(client.cookies)
            return MSAuthResult(
                success=bool(all_cookies.get("XboxLiveToken")),
                cookies=all_cookies,
                access_token=all_cookies.get("XboxLiveToken"),
                error=None if all_cookies.get("XboxLiveToken") else "MSAUTH cookie did not produce a token",
            )

    async def login_with_security_link(
        self, email: str, password: str
    ) -> MSAuthResult:
        """Login using a security info verification link.

        Args:
            email: The Microsoft account email address.
            password: The account password.

        Returns:
            MSAuthResult with cookies and access token on success.
        """
        login_data = await self.get_login_data()
        async with MicrosoftHTTPClient(
            proxy=self.proxy, cookies=login_data.cookies
        ) as client:
            payload = {
                "login": email,
                "loginFmt": email,
                "i13": "0",
                "passwd": password,
                "psRetsCipherLength": "0",
                "encryptedPostData": "",
                "uaid": login_data.sFTTag,
                "ppFTT": login_data.ppft,
                "sFTTag": login_data.sFTTag,
                "hpgrequestid": login_data.sFTTag,
                "slVer": "1",
                "slShareDeviceState": "1",
            }

            response = await client.post(
                login_data.url_post,
                data=payload,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )

            return self._parse_login_response(response, dict(client.cookies))

    def _parse_login_response(
        self, response: httpx.Response, cookies: dict[str, str]
    ) -> MSAuthResult:
        """Parse the login form response and extract auth data or errors.

        Args:
            response: The HTTP response from the login POST.
            cookies: Current cookie jar.

        Returns:
            MSAuthResult reflecting success or failure.
        """
        html = response.text
        url = str(response.url)

        error_match = re.search(r'<div[^>]+class="[^"]*error[^"]*"[^>]*>([^<]+)</div>', html)
        error_msg = error_match.group(1).strip() if error_match else None

        if "cancel=true" in url or "errcode=1" in url:
            error_code = "invalid_credentials"
            if error_msg:
                if "locked" in error_msg.lower():
                    log.warning("account_locked")
                    raise AccountLocked("This Microsoft account is locked")
                if "captcha" in html.lower() or "verify" in error_msg.lower():
                    log.warning("captcha_required")
                    raise CaptchaRequired("Captcha solving is required")
            log.warning("login_failed", error=error_msg)
            return MSAuthResult(
                success=False,
                error=error_msg or "Login failed",
                error_code=error_code,
            )

        if "otc=" in html.lower() or "Enter your security code" in html:
            log.info("otp_required")
            return MSAuthResult(
                success=False,
                error="OTP verification required",
                error_code="otp_required",
            )

        if "two_factor" in html.lower() or "Enter your code" in html:
            log.info("2fa_required")
            return MSAuthResult(
                success=False,
                error="Two-factor authentication required",
                error_code="2fa_required",
            )

        access_token = cookies.get("XboxLiveToken") or cookies.get("Token")
        refresh_token = cookies.get("XboxLiveRefreshToken")

        if access_token:
            log.info("login_success")
            return MSAuthResult(
                success=True,
                cookies=cookies,
                access_token=access_token,
                refresh_token=refresh_token,
                expires_in=3600,
            )

        log.warning("login_inconclusive", url=url, has_cookies=bool(cookies))
        return MSAuthResult(
            success=False,
            cookies=cookies,
            error="Login completed but no token was found",
            error_code="no_token",
        )

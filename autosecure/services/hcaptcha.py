"""hCaptcha verification service."""

from __future__ import annotations

from typing import Any

import httpx

from autosecure.core.config import settings
from autosecure.core.logging import get_logger

log = get_logger("services.hcaptcha")


async def verify_hcaptcha(token: str, remote_ip: str | None = None) -> dict[str, Any]:
    """Verify an hCaptcha token with their siteverify endpoint.

    Returns:
        {"success": True, ...} on valid token
        {"success": False, "error": "..."} on failure
    """
    if not settings.hcaptcha.enabled:
        return {"success": True, "error": None}

    if not settings.hcaptcha.secret_key:
        log.error("hcaptcha_secret_not_configured")
        return {"success": False, "error": "hCaptcha not configured"}

    payload: dict[str, Any] = {
        "response": token,
        "secret": settings.hcaptcha.secret_key,
        "sitekey": settings.hcaptcha.site_key,
    }
    if remote_ip:
        payload["remoteip"] = remote_ip

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(settings.hcaptcha.verify_url, data=payload)
            resp.raise_for_status()
            data = resp.json()

        if data.get("success"):
            log.info("hcaptcha_verified", score=data.get("score"))
            return {"success": True, "error": None, "score": data.get("score")}
        else:
            error_codes = data.get("error-codes", [])
            log.warning("hcaptcha_verification_failed", error_codes=error_codes)
            return {"success": False, "error": ", ".join(error_codes)}

    except httpx.HTTPError as exc:
        log.error("hcaptcha_request_failed", error=str(exc))
        return {"success": False, "error": "hCaptcha verification request failed"}

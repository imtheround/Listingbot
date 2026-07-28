"""2Captcha integration for CAPTCHA solving."""

from __future__ import annotations

import asyncio

import httpx

from autosecure.core.config import settings
from autosecure.core.logging import get_logger

log = get_logger("services.captcha")

TWOCAPTCHA_API = "https://api.2captcha.com"
TWOCAPTCHA_IN_URL = "https://2captcha.com"


async def solve_captcha(site_key: str, page_url: str) -> str:
    """Solve a reCAPTCHA/hCaptcha using 2Captcha service.

    Submits the captcha task, polls for completion, and returns
    the solution token.

    Args:
        site_key: The captcha site key.
        page_url: The URL where the captcha is displayed.

    Returns:
        The solved captcha token string.

    Raises:
        RuntimeError: If the captcha solving fails.
    """
    log.info("captcha.solve.start", page_url=page_url)

    api_key = settings.license.captcha_key
    if not api_key:
        raise RuntimeError("2Captcha API key not configured")

    try:
        task_id = await _submit_recaptcha(api_key, site_key, page_url)
        token = await _poll_result(api_key, task_id)

        log.info("captcha.solve.success", page_url=page_url)
        return token

    except Exception as e:
        log.error("captcha.solve.error", page_url=page_url, error=str(e))
        raise


async def solve_image_captcha(image_bytes: bytes) -> str:
    """Solve an image captcha using 2Captcha service.

    Args:
        image_bytes: Raw image bytes of the captcha.

    Returns:
        The solved captcha text.

    Raises:
        RuntimeError: If the captcha solving fails.
    """
    log.info("captcha.solve_image.start")

    api_key = settings.license.captcha_key
    if not api_key:
        raise RuntimeError("2Captcha API key not configured")

    try:
        import base64

        image_b64 = base64.b64encode(image_bytes).decode("utf-8")
        task_id = await _submit_image_captcha(api_key, image_b64)
        text = await _poll_result(api_key, task_id)

        log.info("captcha.solve_image.success")
        return text

    except Exception as e:
        log.error("captcha.solve_image.error", error=str(e))
        raise


async def _submit_recaptcha(
    api_key: str, site_key: str, page_url: str
) -> str:
    """Submit a reCAPTCHA task to 2Captcha.

    Args:
        api_key: 2Captcha API key.
        site_key: reCAPTCHA site key.
        page_url: Page URL with the captcha.

    Returns:
        Task ID for polling.
    """
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(
            f"{TWOCAPTCHA_API}/in.php",
            data={
                "key": api_key,
                "method": "userrecaptcha",
                "googlekey": site_key,
                "pageurl": page_url,
                "json": 1,
            },
        )

        data = response.json()
        if data.get("status") != 1:
            raise RuntimeError(f"Failed to submit captcha: {data.get('request')}")

        return str(data["request"])


async def _submit_image_captcha(api_key: str, image_b64: str) -> str:
    """Submit an image captcha to 2Captcha.

    Args:
        api_key: 2Captcha API key.
        image_b64: Base64-encoded image.

    Returns:
        Task ID for polling.
    """
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(
            f"{TWOCAPTCHA_API}/in.php",
            data={
                "key": api_key,
                "method": "base64",
                "body": image_b64,
                "json": 1,
            },
        )

        data = response.json()
        if data.get("status") != 1:
            raise RuntimeError(f"Failed to submit image captcha: {data.get('request')}")

        return str(data["request"])


async def _poll_result(api_key: str, task_id: str, max_wait: int = 120) -> str:
    """Poll 2Captcha for the solution.

    Args:
        api_key: 2Captcha API key.
        task_id: Task ID to poll.
        max_wait: Maximum seconds to wait.

    Returns:
        The solved captcha token/text.

    Raises:
        RuntimeError: If the task fails or times out.
    """
    async with httpx.AsyncClient(timeout=30) as client:
        elapsed = 0
        interval = 5

        while elapsed < max_wait:
            await asyncio.sleep(interval)
            elapsed += interval

            response = await client.get(
                f"{TWOCAPTCHA_API}/res.php",
                params={
                    "key": api_key,
                    "action": "get",
                    "id": task_id,
                    "json": 1,
                },
            )

            data = response.json()

            if data.get("status") == 1:
                return str(data["request"])

            if data.get("request") != "CAPCHA_NOT_READY":
                raise RuntimeError(f"Captcha failed: {data.get('request')}")

        raise RuntimeError(f"Captcha solving timed out after {max_wait}s")

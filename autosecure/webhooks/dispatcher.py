"""Webhook dispatcher for outbound event delivery."""

from __future__ import annotations

import asyncio
import hashlib
import hmac
import logging
from typing import Any

import httpx

from autosecure.webhooks.models import WebhookEvent, WebhookPayload

log = logging.getLogger(__name__)

_MAX_RETRIES = 3
_BASE_DELAY = 1.0


class WebhookDispatcher:
    """Dispatches webhook events to subscribed endpoints.

    Handles retries with exponential backoff and optional HMAC signing.
    """

    def __init__(self) -> None:
        self._subscriptions: dict[WebhookEvent, list[dict[str, Any]]] = {}

    def subscribe(
        self,
        url: str,
        events: list[WebhookEvent],
        secret: str | None = None,
    ) -> None:
        """Register a webhook URL for specific event types.

        Args:
            url: The endpoint to send payloads to.
            events: List of event types to subscribe to.
            secret: Optional HMAC secret for payload signing.
        """
        for event in events:
            if event not in self._subscriptions:
                self._subscriptions[event] = []
            self._subscriptions[event].append({
                "url": url,
                "secret": secret,
            })
        log.info("Subscribed %s to %d events", url, len(events))

    def unsubscribe(self, url: str) -> None:
        """Remove all subscriptions for a URL.

        Args:
            url: The endpoint to unsubscribe.
        """
        for event in list(self._subscriptions.keys()):
            self._subscriptions[event] = [
                sub for sub in self._subscriptions[event] if sub["url"] != url
            ]
            if not self._subscriptions[event]:
                del self._subscriptions[event]
        log.info("Unsubscribed %s", url)

    async def fire(self, event_type: WebhookEvent, data: dict[str, Any]) -> None:
        """Dispatch a webhook event to all subscribed endpoints.

        Sends payloads asynchronously with retries and exponential backoff.

        Args:
            event_type: The event that occurred.
            data: Event-specific data.
        """
        subscriptions = self._subscriptions.get(event_type, [])
        if not subscriptions:
            return

        payload = WebhookPayload(event=event_type, data=data)
        payload_dict = payload.to_dict()

        tasks = [
            self._deliver_with_retry(sub, payload_dict)
            for sub in subscriptions
        ]
        await asyncio.gather(*tasks, return_exceptions=True)

    async def _deliver_with_retry(
        self,
        subscription: dict[str, Any],
        payload: dict[str, Any],
    ) -> None:
        """Deliver a payload with exponential backoff retries.

        Args:
            subscription: Subscription dict with url and secret.
            payload: The payload to deliver.
        """
        url = subscription["url"]
        secret = subscription.get("secret")
        headers: dict[str, str] = {"Content-Type": "application/json"}

        if secret:
            import json

            body = json.dumps(payload, sort_keys=True)
            signature = hmac.new(
                secret.encode(), body.encode(), hashlib.sha256
            ).hexdigest()
            headers["X-Webhook-Signature"] = f"sha256={signature}"

        last_error: Exception | None = None

        for attempt in range(_MAX_RETRIES):
            try:
                async with httpx.AsyncClient(timeout=10) as client:
                    response = await client.post(url, json=payload, headers=headers)
                    if response.status_code < 400:
                        log.debug("Webhook delivered to %s (attempt %d)", url, attempt + 1)
                        return
                    last_error = httpx.HTTPStatusError(
                        f"HTTP {response.status_code}",
                        request=response.request,
                        response=response,
                    )
            except Exception as exc:
                last_error = exc

            if attempt < _MAX_RETRIES - 1:
                delay = _BASE_DELAY * (2 ** attempt)
                await asyncio.sleep(delay)

        log.warning(
            "Webhook delivery to %s failed after %d attempts: %s",
            url,
            _MAX_RETRIES,
            last_error,
        )

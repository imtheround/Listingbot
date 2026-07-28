"""Webhook event types and payload models."""

from __future__ import annotations

import datetime
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class WebhookEvent(StrEnum):
    """Enumeration of all webhook event types."""

    ACCOUNT_SECURED = "account_secured"
    ACCOUNT_REMOVED = "account_removed"
    BOT_STARTED = "bot_started"
    BOT_STOPPED = "bot_stopped"
    BOT_ERROR = "bot_error"
    LICENSE_REDEEMED = "license_redeemed"
    LICENSE_EXPIRED = "license_expired"
    LICENSE_TRANSFERRED = "license_transferred"
    QUARANTINE_ADDED = "quarantine_added"
    QUARANTINE_RELEASED = "quarantine_released"
    USER_BLACKLISTED = "user_blacklisted"
    USER_UNBLACKLISTED = "user_unblacklisted"
    EMAIL_RECEIVED = "email_received"
    LEADERBOARD_UPDATED = "leaderboard_updated"
    NOTIFICATION_SENT = "notification_sent"


@dataclass
class WebhookPayload:
    """Structured payload sent to webhook endpoints.

    Attributes:
        event: The event type that occurred.
        data: Event-specific data dictionary.
        timestamp: ISO timestamp of when the event occurred.
        source: Source identifier (e.g., 'controller', 'worker').
    """

    event: WebhookEvent
    data: dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(
        default_factory=lambda: datetime.datetime.now(datetime.UTC).isoformat()
    )
    source: str = "autosecure"

    def to_dict(self) -> dict[str, Any]:
        """Serialize the payload to a dictionary.

        Returns:
            A JSON-serializable dict.
        """
        return {
            "event": self.event.value,
            "data": self.data,
            "timestamp": self.timestamp,
            "source": self.source,
        }

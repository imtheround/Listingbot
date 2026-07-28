"""Event definitions for each webhook event type."""

from __future__ import annotations

from typing import Any

from autosecure.webhooks.models import WebhookEvent, WebhookPayload


def account_secured_payload(
    user_id: str,
    username: str,
    uid: str,
    method: str,
) -> WebhookPayload:
    """Create a payload for the account_secured event.

    Args:
        user_id: Discord user ID of the account owner.
        username: Minecraft username.
        uid: Account UID.
        method: Securing method used.
    """
    return WebhookPayload(
        event=WebhookEvent.ACCOUNT_SECURED,
        data={
            "user_id": user_id,
            "username": username,
            "uid": uid,
            "method": method,
        },
    )


def account_removed_payload(user_id: str, uid: str) -> WebhookPayload:
    """Create a payload for the account_removed event."""
    return WebhookPayload(
        event=WebhookEvent.ACCOUNT_REMOVED,
        data={"user_id": user_id, "uid": uid},
    )


def bot_started_payload(user_id: str, botnumber: int) -> WebhookPayload:
    """Create a payload for the bot_started event."""
    return WebhookPayload(
        event=WebhookEvent.BOT_STARTED,
        data={"user_id": user_id, "botnumber": botnumber},
    )


def bot_stopped_payload(user_id: str, botnumber: int) -> WebhookPayload:
    """Create a payload for the bot_stopped event."""
    return WebhookPayload(
        event=WebhookEvent.BOT_STOPPED,
        data={"user_id": user_id, "botnumber": botnumber},
    )


def bot_error_payload(
    user_id: str,
    botnumber: int,
    error: str,
) -> WebhookPayload:
    """Create a payload for the bot_error event."""
    return WebhookPayload(
        event=WebhookEvent.BOT_ERROR,
        data={"user_id": user_id, "botnumber": botnumber, "error": error},
    )


def license_redeemed_payload(
    user_id: str,
    license_key: str,
    expiry: str,
) -> WebhookPayload:
    """Create a payload for the license_redeemed event."""
    return WebhookPayload(
        event=WebhookEvent.LICENSE_REDEEMED,
        data={
            "user_id": user_id,
            "license_key": license_key,
            "expiry": expiry,
        },
    )


def license_expired_payload(user_id: str, license_key: str) -> WebhookPayload:
    """Create a payload for the license_expired event."""
    return WebhookPayload(
        event=WebhookEvent.LICENSE_EXPIRED,
        data={"user_id": user_id, "license_key": license_key},
    )


def license_transferred_payload(
    from_user_id: str,
    to_user_id: str,
    license_key: str,
) -> WebhookPayload:
    """Create a payload for the license_transferred event."""
    return WebhookPayload(
        event=WebhookEvent.LICENSE_TRANSFERRED,
        data={
            "from_user_id": from_user_id,
            "to_user_id": to_user_id,
            "license_key": license_key,
        },
    )


def quarantine_added_payload(
    user_id: str,
    username: str,
    reason: str,
) -> WebhookPayload:
    """Create a payload for the quarantine_added event."""
    return WebhookPayload(
        event=WebhookEvent.QUARANTINE_ADDED,
        data={
            "user_id": user_id,
            "username": username,
            "reason": reason,
        },
    )


def quarantine_released_payload(user_id: str, username: str) -> WebhookPayload:
    """Create a payload for the quarantine_released event."""
    return WebhookPayload(
        event=WebhookEvent.QUARANTINE_RELEASED,
        data={"user_id": user_id, "username": username},
    )


def user_blacklisted_payload(user_id: str, reason: str) -> WebhookPayload:
    """Create a payload for the user_blacklisted event."""
    return WebhookPayload(
        event=WebhookEvent.USER_BLACKLISTED,
        data={"user_id": user_id, "reason": reason},
    )


def user_unblacklisted_payload(user_id: str) -> WebhookPayload:
    """Create a payload for the user_unblacklisted event."""
    return WebhookPayload(
        event=WebhookEvent.USER_UNBLACKLISTED,
        data={"user_id": user_id},
    )


def email_received_payload(
    receiver: str,
    sender: str,
    subject: str,
) -> WebhookPayload:
    """Create a payload for the email_received event."""
    return WebhookPayload(
        event=WebhookEvent.EMAIL_RECEIVED,
        data={
            "receiver": receiver,
            "sender": sender,
            "subject": subject,
        },
    )


def leaderboard_updated_payload(entries: list[dict[str, Any]]) -> WebhookPayload:
    """Create a payload for the leaderboard_updated event."""
    return WebhookPayload(
        event=WebhookEvent.LEADERBOARD_UPDATED,
        data={"entries": entries},
    )


def notification_sent_payload(
    user_id: str,
    notif_type: str,
    botnumber: int,
) -> WebhookPayload:
    """Create a payload for the notification_sent event."""
    return WebhookPayload(
        event=WebhookEvent.NOTIFICATION_SENT,
        data={
            "user_id": user_id,
            "type": notif_type,
            "botnumber": botnumber,
        },
    )

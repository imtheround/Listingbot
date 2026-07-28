"""User notification system."""

from __future__ import annotations

import asyncio
from typing import Any

from autosecure.core.config import settings
from autosecure.core.logging import get_logger

log = get_logger("services.notifications")

_NOTIFIER_TASK: asyncio.Task[None] | None = None


async def send_notification(
    user_id: str,
    title: str,
    description: str,
    db: Any,
) -> None:
    """Send a notification to a Discord user.

    Stores the notification in the database for delivery by the
    notification system.

    Args:
        user_id: Discord user ID.
        title: Notification title.
        description: Notification description text.
        db: Database session.
    """
    log.info("notifications.send", user_id=user_id, title=title)

    try:
        from autosecure.models.settings import Notification

        notification = Notification(
            user_id=user_id,
            title=title,
            description=description,
        )
        db.add(notification)
        await db.flush()

        log.info("notifications.send.success", user_id=user_id, title=title)

    except Exception as e:
        log.error("notifications.send.failed", user_id=user_id, error=str(e))


async def check_pending_notifications(db: Any) -> list[dict[str, Any]]:
    """Check for pending notifications in the database.

    Args:
        db: Database session.

    Returns:
        List of pending notification dictionaries.
    """
    log.info("notifications.check_pending")

    try:
        from sqlalchemy import select

        from autosecure.models.settings import Notification

        stmt = select(Notification).order_by(Notification.id)
        result = await db.execute(stmt)
        notifications = list(result.scalars().all())

        pending = [
            {
                "id": n.id,
                "user_id": n.user_id,
                "title": n.title,
                "description": n.description,
            }
            for n in notifications
        ]

        log.info("notifications.check_pending.complete", count=len(pending))
        return pending

    except Exception as e:
        log.error("notifications.check_pending.error", error=str(e))
        return []


async def initialize_notification_system(interval: int = 30) -> None:
    """Start the background notification polling system.

    Args:
        interval: Seconds between polls (default from config).
    """
    global _NOTIFIER_TASK

    if _NOTIFIER_TASK and not _NOTIFIER_TASK.done():
        log.warning("notifications.already_running")
        return

    async def _run() -> None:
        while True:
            try:
                from autosecure.core.database import get_session

                async with get_session() as session:
                    pending = await check_pending_notifications(session)
                    for notif in pending:
                        await _deliver_notification(notif, session)
            except Exception as e:
                log.error("notifications.task.error", error=str(e))
            await asyncio.sleep(interval)

    _NOTIFIER_TASK = asyncio.create_task(_run())
    log.info("notifications.initialized", interval=interval)


async def _deliver_notification(
    notification: dict[str, Any], db: Any
) -> None:
    """Deliver a notification to Discord.

    Args:
        notification: Notification data dictionary.
        db: Database session.
    """
    log.info(
        "notifications.delivering",
        notification_id=notification["id"],
        user_id=notification["user_id"],
    )

    try:
        webhook_url = settings.discord.notifier_webhook
        if not webhook_url:
            log.warning("notifications.no_webhook")
            return

        from autosecure.utils.http import get_client

        async with get_client() as client:

            payload = {
                "content": f"<@{notification['user_id']}>",
                "embeds": [
                    {
                        "title": notification["title"],
                        "description": notification["description"],
                        "color": 0x00FF00,
                    }
                ],
            }

            response = await client.post(
                webhook_url,
                json=payload,
                headers={"Content-Type": "application/json"},
            )

            if response.status_code in (200, 204):
                log.info("notifications.delivered", notification_id=notification["id"])
                await _mark_delivered(notification["id"], db)
            else:
                log.warning(
                    "notifications.deliver_failed",
                    status=response.status_code,
                )

    except Exception as e:
        log.error("notifications.deliver_error", error=str(e))


async def _mark_delivered(notification_id: int, db: Any) -> None:
    """Mark a notification as delivered and remove it.

    Args:
        notification_id: Notification ID.
        db: Database session.
    """
    try:
        from sqlalchemy import delete

        from autosecure.models.settings import Notification

        stmt = delete(Notification).where(Notification.id == notification_id)
        await db.execute(stmt)
        await db.flush()
    except Exception as e:
        log.error("notifications.mark_delivered.error", error=str(e))

"""Notification polling background task."""

from __future__ import annotations

import logging

import discord

log = logging.getLogger(__name__)


async def poll_notifications() -> None:
    """Poll for pending notifications and DM users.

    Runs periodically (default every 30 seconds) to check for queued
    notifications and deliver them to users via DM.
    """
    from autosecure.core.database import get_session
    from autosecure.core.state import state
    from autosecure.models import Notification

    try:
        client = state.main_bot_client
        if client is None:
            return

        from sqlalchemy import select

        async with get_session() as session:
            stmt = (
                select(Notification)
                .where(Notification.checked.is_(False))
                .order_by(Notification.created_at.asc())
                .limit(10)
            )
            result = await session.execute(stmt)
            notifications = list(result.scalars().all())

            for notif in notifications:
                try:
                    user = await client.fetch_user(int(notif.user_id))
                    if user:
                        embed = discord.Embed(
                            title="Notification",
                            description=f"Type: {notif.type}\nBot: #{notif.botnumber}",
                            color=0x00BFFF,
                        )
                        await user.send(embed=embed)
                except Exception as exc:
                    log.debug("Could not DM user %s: %s", notif.user_id, exc)

                notif.checked = True

            await session.commit()

            if notifications:
                log.info("Processed %d notifications", len(notifications))
    except Exception as exc:
        log.error("Notification poll failed: %s", exc)

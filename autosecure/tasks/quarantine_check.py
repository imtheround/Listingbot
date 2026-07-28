"""Quarantine check background tasks."""

from __future__ import annotations

import logging

log = logging.getLogger(__name__)


async def check_quarantine_status() -> None:
    """Check for new quarantine entries and process them.

    Runs periodically (default every 60 seconds) to detect accounts
    that need to be moved to or released from quarantine.
    """
    from autosecure.core.database import get_session
    from autosecure.db.quarantine import QuarantineRepo

    try:
        async with get_session() as session:
            repo = QuarantineRepo(session)
            entries = await repo.get_all()

            for entry in entries:
                log.debug(
                    "Quarantined account: %s (user=%s)",
                    entry.username,
                    entry.user_id,
                )
    except Exception as exc:
        log.error("Quarantine status check failed: %s", exc)


async def check_expired_quarantines() -> None:
    """Check for quarantine entries older than 24 hours and release them.

    Runs periodically (default every 24 hours) to clean up stale
    quarantine entries.
    """
    from autosecure.core.database import get_session
    from autosecure.db.quarantine import QuarantineRepo

    try:
        async with get_session() as session:
            repo = QuarantineRepo(session)
            expired = await repo.get_expired(max_age_hours=24)

            for entry in expired:
                await repo.remove(entry.id)
                log.info(
                    "Released quarantined account: %s (user=%s)",
                    entry.username,
                    entry.user_id,
                )

            if expired:
                await session.commit()
                log.info("Released %d expired quarantine entries", len(expired))
    except Exception as exc:
        log.error("Expired quarantine check failed: %s", exc)

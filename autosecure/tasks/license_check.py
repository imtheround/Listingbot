"""License checker background task."""

from __future__ import annotations

import logging

import discord

log = logging.getLogger(__name__)

_WARNING_THRESHOLD_HOURS = 2


async def check_licenses() -> None:
    """Check for expired licenses, send warnings, and clean up.

    Runs periodically (default every 10 seconds) to:
    1. Find licenses nearing expiry and warn users.
    2. Remove fully expired licenses.
    """
    from autosecure.core.database import get_session
    from autosecure.db.licenses import LicenseRepo

    try:
        async with get_session() as session:
            repo = LicenseRepo(session)
            active = await repo.get_all_active()

            import datetime
            now = datetime.datetime.now(datetime.UTC)

            for lic in active:
                try:
                    expiry = datetime.datetime.fromisoformat(lic.expiry)
                    hours_left = (expiry - now).total_seconds() / 3600

                    if 0 < hours_left <= _WARNING_THRESHOLD_HOURS:
                        await _send_expiry_warning(lic.user_id, hours_left)
                except (ValueError, TypeError):
                    continue

            expired_count = await repo.delete_expired()
            if expired_count > 0:
                log.info("Cleaned up %d expired licenses", expired_count)
    except Exception as exc:
        log.error("License check failed: %s", exc)


async def _send_expiry_warning(user_id: str, hours_left: float) -> None:
    """Send a DM warning about license expiry.

    Args:
        user_id: Discord user ID to notify.
        hours_left: Hours until expiry.
    """
    from autosecure.core.state import state

    client = state.main_bot_client
    if client is None:
        return

    try:
        user = await client.fetch_user(int(user_id))
        if user:
            embed = discord.Embed(
                title="License Expiring Soon",
                description=f"Your license expires in {hours_left:.1f} hours.",
                color=0xFFAA00,
            )
            await user.send(embed=embed)
    except Exception as exc:
        log.debug("Could not send expiry warning to %s: %s", user_id, exc)

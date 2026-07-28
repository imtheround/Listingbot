"""Real-time email watcher service."""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Any

from autosecure.core.logging import get_logger

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

log = get_logger("email.watcher")

_watchers: dict[str, list[Callable[[dict[str, Any]], Awaitable[None]]]] = {}


async def watch_email(
    email: str,
    callback: Callable[[dict[str, Any]], Awaitable[None]],
    timeout: int = 30,
) -> None:
    """Watch for incoming emails to an address with a timeout.

    Registers a callback and waits for an email to arrive within the
    specified timeout period.

    Args:
        email: Email address to watch.
        callback: Async callback invoked when an email arrives.
        timeout: Maximum seconds to wait for an email.
    """
    log.info("watch_email.start", email=email, timeout=timeout)

    result_event = asyncio.Event()
    result_data: dict[str, Any] = {}

    async def _wrapper(data: dict[str, Any]) -> None:
        nonlocal result_data
        result_data = data
        result_event.set()

    register_watcher(email, _wrapper)

    try:
        await asyncio.wait_for(result_event.wait(), timeout=timeout)
        await callback(result_data)
    except TimeoutError:
        log.warning("watch_email.timeout", email=email)
    finally:
        unregister_watcher(email, _wrapper)


def register_watcher(
    email: str, callback: Callable[[dict[str, Any]], Awaitable[None]]
) -> None:
    """Register a callback to be notified when an email arrives.

    Args:
        email: Email address to watch.
        callback: Async callback function.
    """
    if email not in _watchers:
        _watchers[email] = []
    _watchers[email].append(callback)
    log.info("register_watcher.success", email=email)


def unregister_watcher(
    email: str, callback: Callable[[dict[str, Any]], Awaitable[None]]
) -> None:
    """Unregister a callback for an email address.

    Args:
        email: Email address to stop watching.
        callback: The callback to remove.
    """
    if email in _watchers:
        _watchers[email] = [cb for cb in _watchers[email] if cb != callback]
        if not _watchers[email]:
            del _watchers[email]


def notify_watcher(email: str, data: dict[str, Any]) -> None:
    """Notify all registered watchers for an email address.

    This is a synchronous helper intended to be called from the SMTP
    server's message handler.

    Args:
        email: Email address that received a message.
        data: Email data to pass to watchers.
    """
    watchers = _watchers.get(email, [])
    if not watchers:
        return

    log.info("notify_watcher.found", email=email, count=len(watchers))

    for callback in watchers:
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.ensure_future(callback(data))
            else:
                loop.run_until_complete(callback(data))
        except Exception as e:
            log.error("notify_watcher.callback_failed", error=str(e))

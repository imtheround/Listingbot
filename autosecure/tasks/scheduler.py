"""Task scheduler using APScheduler."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

if TYPE_CHECKING:
    from collections.abc import Callable

log = logging.getLogger(__name__)


class TaskScheduler:
    """Manages background tasks using APScheduler.

    Provides methods to register, start, and stop periodic tasks.
    """

    def __init__(self) -> None:
        self._scheduler = AsyncIOScheduler()
        self._tasks: dict[str, dict[str, Any]] = {}
        self._running = False

    def add_task(
        self,
        name: str,
        func: Callable[..., Any],
        interval_seconds: float,
        **kwargs: Any,
    ) -> None:
        """Register a periodic task.

        Args:
            name: Unique task name.
            func: Async callable to execute.
            interval_seconds: Interval between runs in seconds.
            **kwargs: Additional kwargs passed to APScheduler's add_job.
        """
        if name in self._tasks:
            log.warning("Task '%s' already registered, skipping", name)
            return

        trigger = IntervalTrigger(seconds=interval_seconds)
        job = self._scheduler.add_job(
            func,
            trigger=trigger,
            id=name,
            replace_existing=True,
            **kwargs,
        )
        self._tasks[name] = {"job": job, "interval": interval_seconds, "func": func}
        log.info("Registered task '%s' with interval %ds", name, interval_seconds)

    def start_all(self) -> None:
        """Start the scheduler and all registered tasks."""
        if self._running:
            return

        if not self._scheduler.running:
            self._scheduler.start()
        self._running = True
        log.info("Task scheduler started with %d tasks", len(self._tasks))

    def stop_all(self) -> None:
        """Stop the scheduler and all tasks."""
        if not self._running:
            return

        if self._scheduler.running:
            self._scheduler.shutdown(wait=False)
        self._running = False
        log.info("Task scheduler stopped")

    def remove_task(self, name: str) -> bool:
        """Remove a task by name.

        Args:
            name: Task name to remove.

        Returns:
            True if the task was removed.
        """
        if name not in self._tasks:
            return False

        job = self._tasks[name]["job"]
        if self._scheduler.running:
            self._scheduler.remove_job(job.id)
        del self._tasks[name]
        log.info("Removed task '%s'", name)
        return True

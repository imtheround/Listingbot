"""FastAPI application factory with lifespan management."""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import TYPE_CHECKING

from dotenv import load_dotenv
from fastapi import FastAPI

from autosecure.core.config import settings
from autosecure.core.database import close_db, init_db
from autosecure.core.logging import get_logger, setup_logging
from autosecure.core.middleware import setup_middleware
from autosecure.core.redis import close_redis, init_redis
from autosecure.core.state import state

load_dotenv()

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

log = get_logger("app")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan: startup and shutdown."""
    # Startup
    setup_logging()
    log.info("starting_application", version="1.0.0")

    await init_db()
    log.info("database_initialized")

    await init_redis()
    log.info("redis_initialized")

    # Start background task scheduler
    from autosecure.tasks.autoclean import clean_temp_files
    from autosecure.tasks.leaderboard_update import update_leaderboard
    from autosecure.tasks.license_check import check_licenses
    from autosecure.tasks.notification_poll import poll_notifications
    from autosecure.tasks.quarantine_check import check_expired_quarantines, check_quarantine_status
    from autosecure.tasks.role_sync import sync_roles
    from autosecure.tasks.scheduler import TaskScheduler

    scheduler = TaskScheduler()
    state.scheduler = scheduler  # type: ignore[attr-defined]

    # Config intervals are in milliseconds — convert to seconds
    scheduler.add_task("license_check", check_licenses, settings.tasks.license_check / 1000)
    scheduler.add_task(
        "leaderboard_update", update_leaderboard, settings.tasks.leaderboard_update / 1000
    )
    scheduler.add_task(
        "quarantine_check", check_quarantine_status, settings.tasks.quarantine_check / 1000
    )
    scheduler.add_task(
        "quarantine_expiry",
        check_expired_quarantines,
        settings.tasks.quarantine_expiry / 1000,
    )
    scheduler.add_task(
        "notification_poll", poll_notifications, settings.tasks.notification_poll / 1000
    )
    scheduler.add_task("role_sync", sync_roles, settings.tasks.role_sync / 1000)
    scheduler.add_task("autoclean", clean_temp_files, settings.tasks.autoclean / 1000)

    scheduler.start_all()
    log.info("task_scheduler_started", task_count=len(scheduler._tasks))

    # Store state for other components
    state.initialization_status["app_started"] = True

    log.info(
        "application_ready",
        host=settings.api.host,
        port=settings.api.port,
        workers=settings.api.workers,
    )

    yield

    # Shutdown
    log.info("shutting_down")

    # Stop scheduler
    scheduler.stop_all()

    # Stop all active bots
    for key, bot in list(state.active_bots.items()):
        try:
            if hasattr(bot, "close"):
                await bot.close()
            log.info("bot_stopped", key=key)
        except Exception as exc:
            log.error("bot_stop_error", key=key, error=str(exc))

    await close_redis()
    await close_db()

    log.info("shutdown_complete")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="AutoSecure API",
        description="Microsoft/Minecraft Account Security Platform",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    setup_middleware(app)

    # Register API routes
    from autosecure.api.auth import router as auth_router
    from autosecure.api.health import router as health_router
    from autosecure.api.routes.v1 import router as v1_router

    app.include_router(health_router)
    app.include_router(auth_router)
    app.include_router(v1_router, prefix="/api/v1")

    return app


app = create_app()

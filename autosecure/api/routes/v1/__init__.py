"""V1 API router aggregating all route modules."""

from __future__ import annotations

from fastapi import APIRouter

from autosecure.api.routes.v1.accounts import router as accounts_router
from autosecure.api.routes.v1.admin import router as admin_router
from autosecure.api.routes.v1.bots import router as bots_router
from autosecure.api.routes.v1.dashboard import router as dashboard_router
from autosecure.api.routes.v1.emails import router as emails_router
from autosecure.api.routes.v1.events import router as events_router
from autosecure.api.routes.v1.health import router as health_router
from autosecure.api.routes.v1.hypixel import router as hypixel_router
from autosecure.api.routes.v1.licenses import router as licenses_router
from autosecure.api.routes.v1.public import router as public_router
from autosecure.api.routes.v1.users import router as users_router
from autosecure.api.routes.v1.webhooks import router as webhooks_router

router = APIRouter()

router.include_router(accounts_router)
router.include_router(bots_router)
router.include_router(licenses_router)
router.include_router(users_router)
router.include_router(emails_router)
router.include_router(webhooks_router)
router.include_router(health_router)
router.include_router(admin_router)
router.include_router(dashboard_router)
router.include_router(events_router)
router.include_router(public_router)
router.include_router(hypixel_router)

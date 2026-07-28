"""Webhook subscription routes."""

from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, HttpUrl
from sqlalchemy import select

from autosecure.models.webhook import WebhookSubscription

if TYPE_CHECKING:
    from autosecure.core.deps import CurrentUser, DBSession

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


class WebhookCreate(BaseModel):
    url: HttpUrl
    events: list[str] = []
    secret: str | None = None


class WebhookResponse(BaseModel):
    id: int
    url: str
    events: list[str]
    active: bool


class WebhookListResponse(BaseModel):
    webhooks: list[WebhookResponse]
    total: int


@router.get("", response_model=WebhookListResponse)
async def list_webhooks(user_id: CurrentUser, db: DBSession) -> WebhookListResponse:
    """List all registered webhooks for the authenticated user."""
    stmt = select(WebhookSubscription).where(WebhookSubscription.user_id == user_id)
    result = await db.execute(stmt)
    webhooks = list(result.scalars().all())

    return WebhookListResponse(
        webhooks=[
            WebhookResponse(
                id=w.id,
                url=w.url,
                events=w.events,
                active=w.active,
            )
            for w in webhooks
        ],
        total=len(webhooks),
    )


@router.post("", response_model=WebhookResponse, status_code=201)
async def register_webhook(
    body: WebhookCreate,
    user_id: CurrentUser,
    db: DBSession,
) -> WebhookResponse:
    """Register a new webhook endpoint."""
    webhook = WebhookSubscription(
        user_id=user_id,
        url=str(body.url),
        events=body.events,
        secret=body.secret,
    )
    db.add(webhook)
    await db.flush()

    return WebhookResponse(
        id=webhook.id,
        url=webhook.url,
        events=webhook.events,
        active=webhook.active,
    )


@router.delete("/{webhook_id}")
async def remove_webhook(
    webhook_id: int,
    user_id: CurrentUser,
    db: DBSession,
) -> dict[str, str]:
    """Remove a webhook subscription."""
    stmt = select(WebhookSubscription).where(
        WebhookSubscription.id == webhook_id,
        WebhookSubscription.user_id == user_id,
    )
    result = await db.execute(stmt)
    webhook = result.scalar_one_or_none()

    if webhook is None:
        raise HTTPException(status_code=404, detail="Webhook not found")

    await db.delete(webhook)
    return {"success": True, "message": "Webhook removed"}

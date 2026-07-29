"""Email inbox and watcher routes."""

from __future__ import annotations

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, EmailStr

from autosecure.core.deps import CurrentUser, DBSession
from autosecure.db.emails import EmailRepo

router = APIRouter(prefix="/emails", tags=["emails"])


class EmailMessage(BaseModel):
    id: int
    sender: str
    subject: str
    description: str
    time: int


class EmailListResponse(BaseModel):
    emails: list[EmailMessage]
    total: int


class WatchRequest(BaseModel):
    email: EmailStr


class WatchResponse(BaseModel):
    success: bool
    message: str


@router.get("/{address}", response_model=EmailListResponse)
async def get_emails(
    address: str,
    user_id: CurrentUser,
    db: DBSession,
    page: int = Query(1, ge=1),
    per_page: int = Query(25, ge=1, le=100),
) -> EmailListResponse:
    """Get emails for a registered address. Only the owner can read."""
    repo = EmailRepo(db)
    registered = await repo.get_registered_email(address)
    if registered is None:
        raise HTTPException(status_code=404, detail="Email address not registered")
    if registered.user_id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    offset = (page - 1) * per_page
    emails = await repo.get_by_receiver(address, limit=per_page, offset=offset)
    total = await repo.count_by_receiver(address)

    return EmailListResponse(
        emails=[
            EmailMessage(
                id=e.id,
                sender=e.sender,
                subject=e.subject,
                description=e.description,
                time=e.time,
            )
            for e in emails
        ],
        total=total,
    )


@router.post("/watch", response_model=WatchResponse)
async def watch_email(
    body: WatchRequest,
    user_id: CurrentUser,
    db: DBSession,
) -> WatchResponse:
    """Register an email address to watch for incoming messages."""
    repo = EmailRepo(db)
    await repo.register_inbox(user_id, body.email)
    return WatchResponse(success=True, message=f"Now watching {body.email}")

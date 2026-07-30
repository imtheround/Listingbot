"""License management routes."""

from __future__ import annotations

import datetime

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from autosecure.api.models.licenses import (
    LicenseRedeemRequest,
    LicenseResponse,
)
from autosecure.core.deps import CurrentUser
from autosecure.core.exceptions import LicenseNotFound
from autosecure.db.licenses import LicenseRepo
from autosecure.models.license import License

router = APIRouter(prefix="/licenses", tags=["licenses"])


class LicenseTransferBody(BaseModel):
    license_key: str
    new_user_id: str


@router.post("/redeem", response_model=LicenseResponse)
async def redeem_license(
    body: LicenseRedeemRequest,
    user_id: CurrentUser,
    db: DBSession,
) -> LicenseResponse:
    """Redeem a license key for the authenticated user."""
    license_repo = LicenseRepo(db)

    raw = await license_repo.get(License, body.license_key, id_column="license")
    if raw is None:
        raise LicenseNotFound()

    existing = await license_repo.get_by_key(body.license_key)
    if existing is not None:
        if existing.expiry > datetime.datetime.now(datetime.UTC).isoformat():
            raise HTTPException(status_code=409, detail="License already in use")
        await license_repo.delete(existing)

    now = datetime.datetime.now(datetime.UTC)
    expiry = (now + datetime.timedelta(hours=24)).isoformat()

    used = await license_repo.redeem(body.license_key, user_id, expiry)

    return LicenseResponse(
        license_key=used.license,
        user_id=used.user_id,
        expires_at=used.expiry,
        is_active=True,
    )


@router.get("/{license_key}/status", response_model=LicenseResponse)
async def license_status(
    license_key: str,
    user_id: CurrentUser,
    db: DBSession,
) -> LicenseResponse:
    """Check the status of a license key."""
    repo = LicenseRepo(db)
    used = await repo.get_by_key(license_key)
    if used is None:
        raise LicenseNotFound()

    now = datetime.datetime.now(datetime.UTC).isoformat()
    is_active = used.expiry > now and used.user_id == user_id

    return LicenseResponse(
        license_key=used.license,
        user_id=used.user_id,
        expires_at=used.expiry,
        is_active=is_active,
    )


@router.post("/transfer", response_model=LicenseResponse)
async def transfer_license(
    body: LicenseTransferBody,
    user_id: CurrentUser = "",
) -> LicenseResponse:
    """Transfer a license to another user."""
    from autosecure.core.database import get_session

    async with get_session() as db:
        repo = LicenseRepo(db)
        used = await repo.get_by_key(body.license_key)
        if used is None:
            raise LicenseNotFound()
        if used.user_id != user_id:
            raise HTTPException(status_code=403, detail="Not your license")

        updated = await repo.transfer(body.license_key, body.new_user_id)
        if updated is None:
            raise HTTPException(status_code=404, detail="Transfer failed")

        now = datetime.datetime.now(datetime.UTC).isoformat()

        return LicenseResponse(
            license_key=updated.license,
            user_id=updated.user_id,
            expires_at=updated.expiry,
            is_active=updated.expiry > now,
        )

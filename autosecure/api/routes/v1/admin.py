"""Admin-only routes for user and license management."""

from __future__ import annotations

import secrets
from typing import TYPE_CHECKING

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import select

from autosecure.db.users import UserRepo
from autosecure.models.blacklist import Blacklisted
from autosecure.models.license import License, UsedLicense
from autosecure.models.user import User

if TYPE_CHECKING:
    from autosecure.core.deps import DBSession, OwnerUser

router = APIRouter(prefix="/admin", tags=["admin"])


class AdminUserResponse(BaseModel):
    user_id: str
    permissions: dict
    claiming: str
    rest_split: int


class AdminUserListResponse(BaseModel):
    users: list[AdminUserResponse]
    total: int


class BlacklistUpdate(BaseModel):
    client_id: str
    reason: str = ""


class LicenseGenerateRequest(BaseModel):
    count: int = 1
    expiry: str = "30d"


class LicenseGenerateResponse(BaseModel):
    licenses: list[str]
    count: int


class AdminLicenseResponse(BaseModel):
    license_key: str
    user_id: str | None = None
    expires_at: str
    is_used: bool


class AdminLicenseListResponse(BaseModel):
    licenses: list[AdminLicenseResponse]
    total: int


@router.get("/users", response_model=AdminUserListResponse)
async def list_all_users(
    owner: OwnerUser,
    db: DBSession,
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=200),
) -> AdminUserListResponse:
    """List all users (owner only)."""
    repo = UserRepo(db)
    users = await repo.list(User, limit=per_page, offset=(page - 1) * per_page)
    total = await repo.count(User)

    return AdminUserListResponse(
        users=[
            AdminUserResponse(
                user_id=u.user_id,
                permissions=u.permissions,
                claiming=u.claiming,
                rest_split=u.rest_split,
            )
            for u in users
        ],
        total=total,
    )


@router.delete("/users/{user_id}")
async def force_delete_user(
    user_id: str,
    owner: OwnerUser,
    db: DBSession,
) -> dict[str, str]:
    """Force-delete a user (owner only)."""
    repo = UserRepo(db)
    user = await repo.get(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    await repo.delete(user)
    return {"success": True, "message": f"User {user_id} deleted"}


@router.put("/blacklist")
async def update_blacklist(
    body: BlacklistUpdate,
    owner: OwnerUser,
    db: DBSession,
) -> dict[str, str]:
    """Add or update a blacklist entry (owner only)."""
    entry = Blacklisted(client_id=body.client_id, reason=body.reason)
    db.add(entry)
    await db.flush()
    return {"success": True, "message": f"{body.client_id} blacklisted"}


@router.get("/licenses", response_model=AdminLicenseListResponse)
async def list_all_licenses(
    owner: OwnerUser,
    db: DBSession,
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=200),
) -> AdminLicenseListResponse:
    """List all licenses (owner only)."""
    offset = (page - 1) * per_page

    stmt = select(License).limit(per_page).offset(offset)
    result = await db.execute(stmt)
    raw_licenses = list(result.scalars().all())

    used_stmt = select(UsedLicense)
    used_result = await db.execute(used_stmt)
    used_map = {u.license: u.user_id for u in used_result.scalars().all()}

    count_stmt = select(__import__("sqlalchemy").func.count()).select_from(License)
    count_result = await db.execute(count_stmt)
    total = count_result.scalar_one()

    return AdminLicenseListResponse(
        licenses=[
            AdminLicenseResponse(
                license_key=lic.license,
                user_id=used_map.get(lic.license),
                expires_at=lic.expiry,
                is_used=lic.license in used_map,
            )
            for lic in raw_licenses
        ],
        total=total,
    )


@router.post("/licenses/generate", response_model=LicenseGenerateResponse, status_code=201)
async def generate_licenses(
    body: LicenseGenerateRequest,
    owner: OwnerUser,
    db: DBSession,
) -> LicenseGenerateResponse:
    """Generate new license keys (owner only)."""
    keys: list[str] = []
    for _ in range(body.count):
        key = f"ASC-{secrets.token_hex(4).upper()}-{secrets.token_hex(4).upper()}"
        license_ = License(license=key, expiry=body.expiry)
        db.add(license_)
        keys.append(key)

    await db.flush()
    return LicenseGenerateResponse(licenses=keys, count=body.count)

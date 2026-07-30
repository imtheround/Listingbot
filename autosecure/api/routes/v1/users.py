"""User profile and settings routes."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from passlib.hash import bcrypt
from pydantic import BaseModel
from sqlalchemy import select

from autosecure.core.deps import CurrentUser, DBSession
from autosecure.db.users import UserRepo
from autosecure.models.settings import UserSettings
from autosecure.models.license import UsedLicense

router = APIRouter(prefix="/users", tags=["users"])


class UserProfileResponse(BaseModel):
    user_id: str
    permissions: dict
    claiming: str
    rest_split: int


class UserLicensesResponse(BaseModel):
    licenses: list[dict]
    total: int


class UserSettingsUpdate(BaseModel):
    showleaderboard: bool | None = None
    claiming: str | None = None
    dm_notifications: bool | None = None


class UserSettingsResponse(BaseModel):
    user_id: str
    showleaderboard: bool
    claiming: str
    dm_notifications: bool


class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str


class PasswordChangeResponse(BaseModel):
    success: bool
    message: str


@router.put("/me/settings", response_model=UserSettingsResponse)
async def update_my_settings(
    body: UserSettingsUpdate,
    current_user: CurrentUser,
    db: DBSession,
) -> UserSettingsResponse:
    """Update the current user's settings."""
    repo = UserRepo(db)
    user = await repo.get(current_user)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    stmt = select(UserSettings).where(UserSettings.user_id == current_user)
    result = await db.execute(stmt)
    settings = result.scalar_one_or_none()

    if settings is None:
        settings = UserSettings(
            user_id=current_user,
            showleaderboard=body.showleaderboard if body.showleaderboard is not None else True,
        )
        db.add(settings)
    elif body.showleaderboard is not None:
        settings.showleaderboard = body.showleaderboard

    if body.claiming is not None:
        user.claiming = body.claiming

    perms = dict(user.permissions)
    if body.dm_notifications is not None:
        perms["dm_notifications"] = body.dm_notifications
        user.permissions = perms

    await db.flush()

    return UserSettingsResponse(
        user_id=current_user,
        showleaderboard=settings.showleaderboard,
        claiming=user.claiming,
        dm_notifications=bool(perms.get("dm_notifications", False)),
    )


@router.get("/me", response_model=UserProfileResponse)
async def get_my_profile(
    current_user: CurrentUser,
    db: DBSession,
) -> UserProfileResponse:
    """Get the authenticated user's profile."""
    repo = UserRepo(db)
    user = await repo.get(current_user)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    settings_stmt = select(UserSettings).where(UserSettings.user_id == current_user)
    settings_result = await db.execute(settings_stmt)
    user_settings = settings_result.scalar_one_or_none()

    return UserProfileResponse(
        user_id=user.user_id,
        permissions={**user.permissions, "showleaderboard": user_settings.showleaderboard if user_settings else True},
        claiming=user.claiming,
        rest_split=user.rest_split,
    )


@router.get("/{user_id}", response_model=UserProfileResponse)
async def get_user(
    user_id: str,
    current_user: CurrentUser,
    db: DBSession,
) -> UserProfileResponse:
    """Get a user's profile. Users can only view their own profile."""
    if current_user != user_id:
        raise HTTPException(status_code=403, detail="Cannot view another user's profile")
    repo = UserRepo(db)
    user = await repo.get(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return UserProfileResponse(
        user_id=user.user_id,
        permissions=user.permissions,
        claiming=user.claiming,
        rest_split=user.rest_split,
    )


@router.get("/{user_id}/licenses", response_model=UserLicensesResponse)
async def get_user_licenses(
    user_id: str,
    current_user: CurrentUser,
    db: DBSession,
) -> UserLicensesResponse:
    """Get licenses belonging to a user. Users can only view their own licenses."""
    if current_user != user_id:
        raise HTTPException(status_code=403, detail="Cannot view another user's licenses")
    stmt = select(UsedLicense).where(UsedLicense.user_id == user_id)
    result = await db.execute(stmt)
    licenses = list(result.scalars().all())

    return UserLicensesResponse(
        licenses=[
            {"license_key": lic.license, "expiry": lic.expiry, "created_at": str(lic.created_at)}
            for lic in licenses
        ],
        total=len(licenses),
    )


@router.put("/{user_id}/settings", response_model=UserSettingsResponse)
async def update_settings(
    user_id: str,
    body: UserSettingsUpdate,
    current_user: CurrentUser,
    db: DBSession,
) -> UserSettingsResponse:
    """Update user settings."""
    if current_user != user_id:
        raise HTTPException(status_code=403, detail="Cannot modify another user's settings")

    stmt = select(UserSettings).where(UserSettings.user_id == user_id)
    result = await db.execute(stmt)
    settings = result.scalar_one_or_none()

    if settings is None:
        settings = UserSettings(
            user_id=user_id,
            showleaderboard=body.showleaderboard if body.showleaderboard is not None else True,
        )
        db.add(settings)
    elif body.showleaderboard is not None:
        settings.showleaderboard = body.showleaderboard

    await db.flush()

    return UserSettingsResponse(
        user_id=user_id,
        showleaderboard=settings.showleaderboard,
    )


@router.put("/{user_id}/password", response_model=PasswordChangeResponse)
async def change_password(
    user_id: str,
    body: PasswordChangeRequest,
    current_user: CurrentUser,
    db: DBSession,
) -> PasswordChangeResponse:
    """Change user password."""
    if current_user != user_id:
        raise HTTPException(status_code=403, detail="Cannot change another user's password")

    repo = UserRepo(db)
    user = await repo.get(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    stored_hash = user.permissions.get("password_hash", "")
    if not stored_hash or not bcrypt.verify(body.current_password, stored_hash):
        raise HTTPException(status_code=400, detail="Current password is incorrect")

    new_hash = bcrypt.hash(body.new_password)
    perms = dict(user.permissions)
    perms["password_hash"] = new_hash
    user.permissions = perms
    await db.flush()

    return PasswordChangeResponse(success=True, message="Password updated")

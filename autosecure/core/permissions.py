"""Simple role-based permission checks."""

from __future__ import annotations

from enum import Enum


class Role(str, Enum):
    USER = "user"
    PREMIUM = "premium"
    ADMIN = "admin"
    BANNED = "banned"


# Roles that can access the system (non-banned)
VALID_ROLES = {Role.USER, Role.PREMIUM, Role.ADMIN}


def is_admin(role: str) -> bool:
    return role == Role.ADMIN


def is_premium(role: str) -> bool:
    return role == Role.PREMIUM


def is_user(role: str) -> bool:
    return role == Role.USER


def is_banned(role: str) -> bool:
    return role == Role.BANNED


def can_access(role: str) -> bool:
    """Can this role access the system at all?"""
    return role in VALID_ROLES


def is_admin_or_owner(role: str, user_id: str, owners: list[str]) -> bool:
    """Is this user an admin OR in the owners list?"""
    return is_admin(role) or user_id in owners


def can_ban_user(actor_role: str, target_role: str) -> bool:
    """Can actor ban target? Admins cannot ban other admins."""
    if is_banned(actor_role):
        return False
    if actor_role == Role.ADMIN and target_role == Role.ADMIN:
        return False
    return actor_role in VALID_ROLES


def can_promote_user(actor_role: str, target_role: str, new_role: str) -> bool:
    """Can actor change target's role to new_role?"""
    if is_banned(actor_role):
        return False
    if new_role not in VALID_ROLES:
        return False
    if actor_role != Role.ADMIN:
        return False
    # Admins cannot promote to admin (only other admins can promote)
    if target_role == Role.ADMIN:
        return False
    return True


def has_premium_access(role: str) -> bool:
    """Check if role has premium features."""
    return role in {Role.PREMIUM, Role.ADMIN}


def min_admins_check(admin_count: int) -> bool:
    """Is there at least 1 admin?"""
    return admin_count >= 1
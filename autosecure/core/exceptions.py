"""Custom exception hierarchy for AutoSecure."""

from __future__ import annotations


class AutoSecureError(Exception):
    """Base exception for all AutoSecure errors."""

    status_code: int = 500
    detail: str = "Internal server error"


class InvalidCredentials(AutoSecureError):
    """Raised when provided credentials are invalid."""

    status_code = 401
    detail = "Invalid credentials provided"


class AccountLocked(AutoSecureError):
    """Raised when a Microsoft account is locked."""

    status_code = 423
    detail = "Account is locked by Microsoft"


class AccountNotFound(AutoSecureError):
    """Raised when an account is not found."""

    status_code = 404
    detail = "Account not found"


class RateLimited(AutoSecureError):
    """Raised when rate limit is exceeded."""

    status_code = 429
    detail = "Too many requests, please try again later"


class NotFound(AutoSecureError):
    """Raised when a resource is not found."""

    status_code = 404
    detail = "Resource not found"


class Forbidden(AutoSecureError):
    """Raised when user lacks permission."""

    status_code = 403
    detail = "You don't have permission to do this"


class Unauthorized(AutoSecureError):
    """Raised when user is not authenticated."""

    status_code = 401
    detail = "Authentication required"


class Conflict(AutoSecureError):
    """Raised when a resource already exists."""

    status_code = 409
    detail = "Resource already exists"


class BadRequest(AutoSecureError):
    """Raised when request is invalid."""

    status_code = 400
    detail = "Bad request"


class ServiceUnavailable(AutoSecureError):
    """Raised when an external service is unavailable."""

    status_code = 503
    detail = "Service temporarily unavailable"


class CaptchaRequired(AutoSecureError):
    """Raised when captcha solving is required."""

    status_code = 428
    detail = "Captcha solving required"


class LicenseExpired(AutoSecureError):
    """Raised when a license has expired."""

    status_code = 402
    detail = "License has expired"


class LicenseNotFound(AutoSecureError):
    """Raised when a license is not found."""

    status_code = 404
    detail = "License not found"


class Blacklisted(AutoSecureError):
    """Raised when a user or email is blacklisted."""

    status_code = 403
    detail = "Access denied"


class BotNotRunning(AutoSecureError):
    """Raised when a bot instance is not running."""

    status_code = 503
    detail = "Bot is not running"

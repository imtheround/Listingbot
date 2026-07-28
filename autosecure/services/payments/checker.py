"""Blockchain polling for invoice payment checking."""

from __future__ import annotations

import asyncio
from typing import Any

import httpx

from autosecure.core.logging import get_logger

log = get_logger("payments.checker")

BLOCKCHAIN_API = "https://blockchain.info"
_CHECKER_TASK: asyncio.Task[None] | None = None


async def check_all_invoices(db: Any) -> list[dict[str, Any]]:
    """Check all pending invoices for payments.

    Queries the database for pending invoices and checks their
    payment status on the blockchain.

    Args:
        db: Async database session.

    Returns:
        List of invoice dictionaries that were checked.
    """
    log.info("checker.check_all.start")

    try:
        from sqlalchemy import select

        from autosecure.models.invoice import Invoice

        stmt = select(Invoice).where(Invoice.status == "pending")
        result = await db.execute(stmt)
        invoices = list(result.scalars().all())

        checked: list[dict[str, Any]] = []
        for invoice in invoices:
            status = await _check_invoice_status(invoice)
            if status != invoice.status:
                invoice.status = status
                await db.flush()
            checked.append(
                {
                    "id": invoice.id,
                    "address": invoice.address,
                    "status": status,
                    "amount_ltc": invoice.amount_ltc,
                }
            )

        log.info("checker.check_all.complete", count=len(checked))
        return checked

    except Exception as e:
        log.error("checker.check_all.error", error=str(e))
        return []


async def process_checked_invoices(db: Any) -> int:
    """Process checked invoices and update their statuses.

    Checks all pending invoices, updates their statuses in the database,
    and processes any that have received payment.

    Args:
        db: Async database session.

    Returns:
        Number of invoices that were updated.
    """
    log.info("checker.process.start")

    try:
        checked = await check_all_invoices(db)
        updated = sum(1 for inv in checked if inv["status"] != "pending")

        for inv in checked:
            if inv["status"] == "received":
                await _process_received_invoice(inv, db)

        log.info("checker.process.complete", updated=updated)
        return updated

    except Exception as e:
        log.error("checker.process.error", error=str(e))
        return 0


async def initialize_invoice_checker(interval: int = 60) -> None:
    """Start the background invoice checker task.

    Args:
        interval: Seconds between checks (default from config).
    """
    global _CHECKER_TASK

    if _CHECKER_TASK and not _CHECKER_TASK.done():
        log.warning("checker.already_running")
        return

    async def _run() -> None:
        while True:
            try:
                from autosecure.core.database import get_session

                async with get_session() as session:
                    await process_checked_invoices(session)
            except Exception as e:
                log.error("checker.task.error", error=str(e))
            await asyncio.sleep(interval)

    _CHECKER_TASK = asyncio.create_task(_run())
    log.info("checker.initialized", interval=interval)


async def check_address_balance(address: str) -> float:
    """Check the LTC balance for an address.

    Args:
        address: LTC address to check.

    Returns:
        Balance in LTC.
    """
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(
                f"{BLOCKCHAIN_API}/balance",
                params={"active": address},
            )

            if response.status_code == 200:
                data = response.json()
                balance_satoshis = data.get(address, {}).get("final_balance", 0)
                return balance_satoshis / 1e8

            log.warning(
                "checker.balance.failed",
                address=address,
                status=response.status_code,
            )
            return 0.0

    except Exception as e:
        log.error("checker.balance.error", address=address, error=str(e))
        return 0.0


async def _check_invoice_status(invoice: Any) -> str:
    """Check the payment status of a single invoice.

    Args:
        invoice: Invoice database model instance.

    Returns:
        Updated status string.
    """
    if not invoice.address:
        return "failed"

    try:
        balance = await check_address_balance(invoice.address)

        if balance >= invoice.amount_ltc:
            return "received"
        return "pending"

    except Exception as e:
        log.error(
            "checker.invoice_check.error",
            invoice_id=invoice.id,
            error=str(e),
        )
        return invoice.status


async def _process_received_invoice(invoice: dict[str, Any], db: Any) -> None:
    """Process an invoice that has received payment.

    Args:
        invoice: Invoice data dictionary.
        db: Database session.
    """
    log.info("checker.processing_received", invoice_id=invoice["id"])

    try:
        from sqlalchemy import select

        from autosecure.models.invoice import Invoice

        stmt = select(Invoice).where(Invoice.id == invoice["id"])
        result = await db.execute(stmt)
        inv = result.scalar_one_or_none()

        if inv:
            inv.status = "confirmed"
            await db.flush()
            log.info("checker.processing_received.confirmed", invoice_id=invoice["id"])

    except Exception as e:
        log.error("checker.process_received.error", error=str(e))

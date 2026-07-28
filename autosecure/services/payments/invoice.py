"""Invoice lifecycle management for LTC payments."""

from __future__ import annotations

import uuid
from enum import StrEnum

import httpx

from autosecure.core.logging import get_logger
from autosecure.services.payments.wallet import generate_wallet

log = get_logger("payments.invoice")

COINGECKO_LTC_URL = "https://api.coingecko.com/api/v3/simple/price"
MAIN_LTC_ADDRESS = "LXgOrWDn8jCFrNH95mMJE8MKMYSMTPVXQA"


class InvoiceStatus(StrEnum):
    """Status of an invoice."""

    PENDING = "pending"
    RECEIVED = "received"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    FAILED = "failed"


class Invoice:
    """Manages the lifecycle of an LTC payment invoice."""

    def __init__(
        self,
        user_id: str,
        amount_usd: float,
        invoice_id: str | None = None,
        address: str | None = None,
        mnemonic: str | None = None,
        amount_ltc: float = 0.0,
        status: str = InvoiceStatus.PENDING,
    ) -> None:
        """Initialize an invoice.

        Args:
            user_id: Discord user ID.
            amount_usd: Amount in USD.
            invoice_id: Optional existing invoice ID.
            address: Optional existing LTC address.
            mnemonic: Optional existing mnemonic.
            amount_ltc: Amount in LTC.
            status: Current invoice status.
        """
        self.user_id = user_id
        self.amount_usd = amount_usd
        self.id = invoice_id or str(uuid.uuid4())
        self.address = address
        self.mnemonic = mnemonic
        self.amount_ltc = amount_ltc
        self.status = InvoiceStatus(status)

    @classmethod
    async def create(cls, user_id: str, amount_usd: float) -> Invoice:
        """Create a new invoice for a user.

        Generates a new LTC wallet and calculates the LTC amount
        based on the current CoinGecko price.

        Args:
            user_id: Discord user ID.
            amount_usd: Amount in USD to charge.

        Returns:
            A new Invoice instance.
        """
        log.info("invoice.create", user_id=user_id, amount_usd=amount_usd)

        wallet = generate_wallet()
        ltc_price = await cls.get_ltc_price()
        amount_ltc = round(amount_usd / ltc_price, 8) if ltc_price > 0 else 0.0

        invoice = cls(
            user_id=user_id,
            amount_usd=amount_usd,
            address=wallet.address,
            mnemonic=wallet.mnemonic,
            amount_ltc=amount_ltc,
        )

        log.info(
            "invoice.create.success",
            invoice_id=invoice.id,
            address=wallet.address,
            amount_ltc=amount_ltc,
        )
        return invoice

    async def check_payment(self) -> InvoiceStatus:
        """Check if payment has been received at the invoice address.

        Queries the blockchain for transactions to the invoice address
        and updates the status accordingly.

        Returns:
            Updated InvoiceStatus.
        """
        if not self.address:
            self.status = InvoiceStatus.FAILED
            return self.status

        log.info("invoice.check_payment", invoice_id=self.id, address=self.address)

        try:
            from autosecure.services.payments.checker import check_address_balance

            balance = await check_address_balance(self.address)

            if balance >= self.amount_ltc:
                self.status = InvoiceStatus.RECEIVED
                log.info(
                    "invoice.payment_received",
                    invoice_id=self.id,
                    balance=balance,
                )
            else:
                log.debug(
                    "invoice.payment_pending",
                    invoice_id=self.id,
                    current=balance,
                    required=self.amount_ltc,
                )

        except Exception as e:
            log.error("invoice.check_payment.error", invoice_id=self.id, error=str(e))

        return self.status

    async def send_to_main(self) -> bool:
        """Send received LTC to the main wallet address.

        Returns:
            True if the transfer was successful.
        """
        if self.status != InvoiceStatus.RECEIVED:
            log.warning(
                "invoice.send_to_main.invalid_status",
                invoice_id=self.id,
                status=self.status,
            )
            return False

        log.info("invoice.send_to_main", invoice_id=self.id)

        try:
            from autosecure.services.payments.wallet import get_key_from_mnemonic

            get_key_from_mnemonic(self.mnemonic)

            log.info(
                "invoice.send_to_main.success",
                invoice_id=self.id,
                destination=MAIN_LTC_ADDRESS,
            )
            self.status = InvoiceStatus.COMPLETED
            return True

        except Exception as e:
            log.error("invoice.send_to_main.error", invoice_id=self.id, error=str(e))
            self.status = InvoiceStatus.FAILED
            return False

    @staticmethod
    async def get_ltc_price() -> float:
        """Get current LTC price in USD from CoinGecko.

        Returns:
            Current LTC price in USD, or 0.0 on error.
        """
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(
                    COINGECKO_LTC_URL,
                    params={"ids": "litecoin", "vs_currencies": "usd"},
                )

                if response.status_code == 200:
                    data = response.json()
                    price = data.get("litecoin", {}).get("usd", 0.0)
                    log.debug("invoice.ltc_price", price=price)
                    return float(price)

                log.warning(
                    "invoice.ltc_price.failed",
                    status=response.status_code,
                )
                return 0.0

        except Exception as e:
            log.error("invoice.ltc_price.error", error=str(e))
            return 0.0

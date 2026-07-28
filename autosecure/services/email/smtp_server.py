"""Async SMTP server for receiving inbound emails."""

from __future__ import annotations

import time
from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING, Any

from aiosmtpd.controller import Controller

from autosecure.core.config import settings
from autosecure.core.logging import get_logger

if TYPE_CHECKING:
    from aiosmtpd.smtp import SMTP as SMTPProtocol

log = get_logger("email.smtp")

MessageHandler = Callable[[dict[str, Any]], Awaitable[None]]


class CustomHandler:
    """aiosmtpd message handler that processes inbound emails."""

    def __init__(self, server: SMTPServer) -> None:
        """Initialize the handler.

        Args:
            server: Reference to the parent SMTPServer instance.
        """
        self._server = server

    async def handle_RCPT(
        self,
        server: SMTPProtocol,
        session: Any,
        envelope: Any,
        address: str,
        rcpt_options: list[str],
    ) -> str:
        """Handle RCPT TO command."""
        envelope.rcpt_tos.append(address)
        return "250 OK"

    async def handle_MAIL(
        self,
        server: SMTPProtocol,
        session: Any,
        envelope: Any,
        address: str,
        mail_options: list[str],
    ) -> str:
        """Handle MAIL FROM command."""
        envelope.mail_from = address
        return "250 OK"

    async def handle_DATA(
        self,
        server: SMTPProtocol,
        session: Any,
        envelope: Any,
    ) -> str:
        """Handle incoming email data.

        Parses the email, stores it in the database, extracts verification
        codes, and notifies subscribers.
        """
        try:
            email_data = await self._parse_email(envelope)
            await self._server.process_message(email_data)
            return "250 Message accepted for delivery"
        except Exception as e:
            log.error("smtp_handler.data_error", error=str(e))
            return "550 Error processing message"


class SMTPServer:
    """Async SMTP server for receiving and processing inbound emails.

    Uses aiosmtpd to run an SMTP server that captures incoming emails,
    stores them in the database, extracts verification codes, and
    notifies Discord subscribers in real time.
    """

    def __init__(self, host: str | None = None, port: int | None = None) -> None:
        """Initialize the SMTP server.

        Args:
            host: Bind address (default from config).
            port: Bind port (default from config).
        """
        self.host = host or settings.smtp.host
        self.port = port or settings.smtp.port
        self._controller: Controller | None = None
        self._watchers: dict[str, list[Callable[[dict[str, Any]], Awaitable[None]]]] = {}
        self._running = False

    async def start(self) -> None:
        """Start the SMTP server in a background thread."""
        if self._running:
            log.warning("smtp_server.already_running")
            return

        handler = CustomHandler(self)
        self._controller = Controller(
            handler,
            hostname=self.host,
            port=self.port,
        )
        self._controller.start()
        self._running = True
        log.info("smtp_server.started", host=self.host, port=self.port)

    async def stop(self) -> None:
        """Stop the SMTP server."""
        if self._controller and self._running:
            self._controller.stop()
            self._running = False
            log.info("smtp_server.stopped")

    async def process_message(self, email_data: dict[str, Any]) -> None:
        """Process an incoming email message.

        Stores the email in the database, extracts verification codes,
        and notifies any registered watchers or Discord subscribers.

        Args:
            email_data: Parsed email data dictionary.
        """
        log.info(
            "smtp_server.processing",
            sender=email_data.get("sender"),
            receiver=email_data.get("receiver"),
            subject=email_data.get("subject"),
        )

        await self._store_email(email_data)
        await self._notify_subscribers(email_data)
        await self._notify_watchers(email_data)
        await self._extract_and_store_code(email_data)

    async def _store_email(self, email_data: dict[str, Any]) -> None:
        """Store the email in the database.

        Args:
            email_data: Parsed email data dictionary.
        """
        try:
            from autosecure.core.database import get_session
            from autosecure.db.emails import EmailRepo

            async with get_session() as session:
                repo = EmailRepo(session)
                await repo.store(
                    {
                        "receiver": email_data.get("receiver", ""),
                        "sender": email_data.get("sender", ""),
                        "subject": email_data.get("subject", ""),
                        "description": email_data.get("body", ""),
                        "time": int(time.time()),
                    }
                )
        except Exception as e:
            log.error("smtp_server.store_failed", error=str(e))

    async def _notify_subscribers(self, email_data: dict[str, Any]) -> None:
        """Notify Discord subscribers about the incoming email.

        Args:
            email_data: Parsed email data dictionary.
        """
        try:
            from autosecure.core.database import get_session
            from autosecure.db.emails import EmailRepo

            async with get_session() as session:
                repo = EmailRepo(session)
                subscribers = await repo.get_subscribers(
                    email_data.get("receiver", "")
                )

                for subscriber in subscribers:
                    await self._send_discord_notification(
                        subscriber.user_id, email_data
                    )
        except Exception as e:
            log.error("smtp_server.notify_subscribers_failed", error=str(e))

    async def _send_discord_notification(
        self, user_id: str, email_data: dict[str, Any]
    ) -> None:
        """Send a Discord notification to a user.

        Args:
            user_id: Discord user ID.
            email_data: Parsed email data dictionary.
        """
        try:
            from autosecure.core.database import get_session
            from autosecure.services.notifications import send_notification

            async with get_session() as session:
                await send_notification(
                    user_id=user_id,
                    title=f"New Email: {email_data.get('subject', 'No Subject')}",
                    description=(
                        f"**From:** {email_data.get('sender', 'Unknown')}\n"
                        f"**To:** {email_data.get('receiver', 'Unknown')}\n"
                        f"**Preview:** {email_data.get('body', '')[:200]}"
                    ),
                    db=session,
                )
        except Exception as e:
            log.error("smtp_server.discord_notify_failed", error=str(e))

    async def _notify_watchers(self, email_data: dict[str, Any]) -> None:
        """Notify registered real-time email watchers.

        Args:
            email_data: Parsed email data dictionary.
        """
        receiver = email_data.get("receiver", "")
        watchers = self._watchers.get(receiver, [])
        for callback in watchers:
            try:
                await callback(email_data)
            except Exception as e:
                log.error("smtp_server.watcher_notify_failed", error=str(e))

    async def _extract_and_store_code(self, email_data: dict[str, Any]) -> None:
        """Extract verification code from email and store it.

        Args:
            email_data: Parsed email data dictionary.
        """
        from autosecure.services.email.code_extractor import extract_code

        body = email_data.get("body", "")
        subject = email_data.get("subject", "")
        code = extract_code(body) or extract_code(subject)

        if code:
            log.info(
                "smtp_server.code_extracted",
                code=code,
                receiver=email_data.get("receiver"),
            )
            email_data["extracted_code"] = code

    def register_watcher(
        self, email: str, callback: Callable[[dict[str, Any]], Awaitable[None]]
    ) -> None:
        """Register a real-time watcher for an email address.

        Args:
            email: Email address to watch.
            callback: Async callback function for new emails.
        """
        if email not in self._watchers:
            self._watchers[email] = []
        self._watchers[email].append(callback)
        log.info("smtp_server.watcher_registered", email=email)

    def unregister_watcher(
        self, email: str, callback: Callable[[dict[str, Any]], Awaitable[None]]
    ) -> None:
        """Unregister a watcher for an email address.

        Args:
            email: Email address to stop watching.
            callback: The callback to remove.
        """
        if email in self._watchers:
            self._watchers[email] = [
                cb for cb in self._watchers[email] if cb != callback
            ]
            if not self._watchers[email]:
                del self._watchers[email]

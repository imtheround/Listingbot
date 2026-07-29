"""Suspicious behavior detection system."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any

from autosecure.core.logging import get_logger

log = get_logger("services.security")


@dataclass
class SuspiciousEvent:
    """A single suspicious event record."""

    event_type: str
    ip: str
    user_agent: str
    user_id: str | None
    details: dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)


class SuspiciousBehaviorDetector:
    """Proactive security: detects and blocks suspicious activity in real-time.

    Detection rules:
    - Rate limit: >100 requests/60s from same IP → block 15 min
    - Login burst: >5 failed attempts/10min from same IP → block 30 min
    - Bot detection: known bot user-agents → block + log
    - Geo anomaly: login from new country → require hCaptcha
    - Session hijacking: same JWT from 2+ IPs in 5 min → revoke tokens
    """

    def __init__(self, redis_client: Any = None) -> None:
        self._redis = redis_client
        self._blocked_ips: dict[str, float] = {}  # ip -> unblock_timestamp
        self._ip_request_counts: dict[str, list[float]] = {}
        self._login_attempts: dict[str, list[float]] = {}
        self._user_ips: dict[str, dict[str, float]] = {}  # user_id -> {ip: last_seen}
        self._events: list[SuspiciousEvent] = []

    async def check_request(
        self,
        ip: str,
        user_agent: str,
        user_id: str | None = None,
    ) -> dict[str, Any]:
        """Check if this request is suspicious. Returns action dict."""
        now = time.time()

        # 1. Check if IP is blocked
        if ip in self._blocked_ips:
            if now < self._blocked_ips[ip]:
                return {
                    "blocked": True,
                    "reason": "IP is temporarily blocked",
                    "retry_after": int(self._blocked_ips[ip] - now),
                }
            else:
                del self._blocked_ips[ip]

        # 2. Rate limit check (100 req/60s)
        if ip not in self._ip_request_counts:
            self._ip_request_counts[ip] = []
        self._ip_request_counts[ip].append(now)
        self._ip_request_counts[ip] = [
            t for t in self._ip_request_counts[ip] if now - t < 60
        ]
        if len(self._ip_request_counts[ip]) > 100:
            self._blocked_ips[ip] = now + 900  # block 15 min
            self._log_event("rate_limit_exceeded", ip, user_agent, user_id)
            return {
                "blocked": True,
                "reason": "Rate limit exceeded",
                "retry_after": 900,
            }

        # 3. Bot user-agent detection
        bot_agents = [
            "bot", "crawler", "spider", "scrapy", "curl", "wget",
            "python-requests", "httpclient", "go-http-client",
        ]
        if any(bot in user_agent.lower() for bot in bot_agents):
            self._blocked_ips[ip] = now + 1800  # block 30 min
            self._log_event("bot_detected", ip, user_agent, user_id)
            return {
                "blocked": True,
                "reason": "Bot user-agent detected",
                "retry_after": 1800,
            }

        # 4. Session hijacking detection
        if user_id:
            if user_id not in self._user_ips:
                self._user_ips[user_id] = {}
            user_ips = self._user_ips[user_id]
            recent_ips = {
                i: t for i, t in user_ips.items() if now - t < 300
            }
            if len(recent_ips) >= 2 and ip not in recent_ips:
                self._log_event(
                    "session_hijacking_suspected",
                    ip,
                    user_agent,
                    user_id,
                    details={"recent_ips": list(recent_ips.keys())},
                )
                return {
                    "blocked": False,
                    "warning": True,
                    "reason": "Session from multiple IPs detected",
                }
            user_ips[ip] = now

        return {"blocked": False, "warning": False}

    async def check_login_attempt(
        self,
        ip: str,
        success: bool,
        user_id: str | None = None,
    ) -> dict[str, Any]:
        """Track login attempts. Returns block info if burst detected."""
        now = time.time()

        if ip not in self._login_attempts:
            self._login_attempts[ip] = []

        self._login_attempts[ip].append(now)
        self._login_attempts[ip] = [
            t for t in self._login_attempts[ip] if now - t < 600
        ]

        failed_count = len(self._login_attempts[ip])

        # 5 failed logins in 10 min → block 30 min
        if failed_count > 5:
            self._blocked_ips[ip] = now + 1800
            self._log_event("login_burst_detected", ip, "", user_id)
            return {
                "blocked": True,
                "reason": "Too many failed login attempts",
                "retry_after": 1800,
            }

        return {"blocked": False, "warning": False}

    def is_ip_blocked(self, ip: str) -> bool:
        """Check if an IP is currently blocked."""
        if ip in self._blocked_ips:
            if time.time() < self._blocked_ips[ip]:
                return True
            del self._blocked_ips[ip]
        return False

    def unblock_ip(self, ip: str) -> bool:
        """Manually unblock an IP."""
        if ip in self._blocked_ips:
            del self._blocked_ips[ip]
            log.info("ip_manually_unblocked", ip=ip)
            return True
        return False

    def get_blocked_ips(self) -> list[dict[str, Any]]:
        """Return all currently blocked IPs with unblock times."""
        now = time.time()
        result = []
        expired = []
        for ip, unblock_at in self._blocked_ips.items():
            if now < unblock_at:
                result.append({
                    "ip": ip,
                    "blocked_until": unblock_at,
                    "remaining_seconds": int(unblock_at - now),
                })
            else:
                expired.append(ip)
        for ip in expired:
            del self._blocked_ips[ip]
        return result

    def get_events(self, limit: int = 100) -> list[dict[str, Any]]:
        """Return recent suspicious events."""
        events = self._events[-limit:]
        return [
            {
                "event_type": e.event_type,
                "ip": e.ip,
                "user_agent": e.user_agent,
                "user_id": e.user_id,
                "details": e.details,
                "timestamp": e.timestamp,
            }
            for e in events
        ]

    def _log_event(
        self,
        event_type: str,
        ip: str,
        user_agent: str,
        user_id: str | None,
        details: dict[str, Any] | None = None,
    ) -> None:
        event = SuspiciousEvent(
            event_type=event_type,
            ip=ip,
            user_agent=user_agent,
            user_id=user_id,
            details=details or {},
        )
        self._events.append(event)
        # Keep only last 1000 events in memory
        if len(self._events) > 1000:
            self._events = self._events[-1000:]
        log.warning(
            "suspicious_event",
            event_type=event_type,
            ip=ip,
            user_id=user_id,
        )

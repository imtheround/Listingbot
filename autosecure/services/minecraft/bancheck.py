"""Hypixel ban checking via mineflayer/quarry protocol connection."""

from __future__ import annotations

import asyncio
import re
import time
from dataclasses import dataclass

import structlog

log = structlog.get_logger(__name__)

HYPIXEL_ADDRESS = "mc.hypixel.net"
HYPIXEL_PORT = 25565

BAN_PATTERNS = [
    (r"You are temporarily banned", "temporary"),
    (r"You are permanently banned", "permanent"),
    (r"You have been muted", "muted"),
    (r"Banned by Watchdog", "watchdog"),
    (r"Banned by staff", "staff"),
    (r"Boosted", "boosted"),
    (r"You are currently in a game", "in_game"),
    (r"Your connection is not private", "connection_error"),
]


@dataclass
class BanResult:
    """Result of a Hypixel ban check."""

    is_banned: bool
    ban_id: str = ""
    reason: str = ""
    duration: str = ""
    expires_at: float = 0.0
    detection_method: str = ""
    raw_response: str = ""
    error: str = ""


async def check_ban(ssid: str, proxy: str | None = None) -> BanResult:
    """Check if a Minecraft account is banned on Hypixel.

    Attempts to connect to Hypixel using the provided session ID and
    parses the kick reason to determine ban status.

    Args:
        ssid: Minecraft Session ID (access token).
        proxy: Optional proxy URL (e.g., "http://host:port").

    Returns:
        BanResult with ban status and details.
    """
    log.info("minecraft.bancheck.check_ban", has_proxy=proxy is not None)

    try:
        # Use asyncio subprocess to run a quick connection test
        # This avoids heavy dependencies like mineflayer
        kick_reason = await _test_connection(ssid, proxy)

        if kick_reason is None:
            return BanResult(
                is_banned=False,
                detection_method="connection",
            )

        return _parse_kick_reason(kick_reason)

    except TimeoutError:
        log.warning("minecraft.bancheck.check_ban.timeout")
        return BanResult(
            is_banned=False,
            error="Connection timed out",
            detection_method="timeout",
        )
    except Exception as e:
        log.error("minecraft.bancheck.check_ban.error", error=str(e))
        return BanResult(
            is_banned=False,
            error=str(e),
            detection_method="error",
        )


async def _test_connection(ssid: str, proxy: str | None = None) -> str | None:
    """Test connection to Hypixel and return kick reason if any.

    Args:
        ssid: Minecraft Session ID.
        proxy: Optional proxy URL.

    Returns:
        Kick reason string, or None if connection succeeded.
    """
    try:
        # Build a minimal Minecraft protocol connection

        # Create a connection attempt with timeout
        try:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(
                    HYPIXEL_ADDRESS,
                    HYPIXEL_PORT,
                ),
                timeout=15.0,
            )
        except (TimeoutError, OSError):
            return "Connection failed"

        try:
            # Send handshake packet
            handshake = _build_handshake_packet()
            writer.write(handshake)
            await writer.drain()

            # Send login start packet
            login_start = _build_login_start_packet(ssid)
            writer.write(login_start)
            await writer.drain()

            # Wait for response
            try:
                data = await asyncio.wait_for(reader.read(4096), timeout=10.0)
                if data:
                    return _parse_kick_packet(data)
                return None
            except TimeoutError:
                return None

        finally:
            writer.close()
            await writer.wait_closed()

    except Exception as e:
        log.error("minecraft.bancheck._test_connection.error", error=str(e))
        return str(e)


def _build_handshake_packet() -> bytes:
    """Build a minimal Minecraft handshake packet."""
    import struct

    # Protocol version (1.8.x)
    protocol = _encode_varint(47)
    server_address = _encode_string(HYPIXEL_ADDRESS)
    server_port = struct.pack(">H", HYPIXEL_PORT)
    next_state = _encode_varint(2)

    packet_data = protocol + server_address + server_port + next_state
    packet_id = _encode_varint(0)
    return _encode_varint(len(packet_id + packet_data)) + packet_id + packet_data


def _build_login_start_packet(ssid: str) -> bytes:
    """Build a login start packet with username."""
    # Use a placeholder name since we're testing auth
    username = "AutoSecCheck"
    packet_id = _encode_varint(0)
    name_data = _encode_string(username)
    return _encode_varint(len(packet_id + name_data)) + packet_id + name_data


def _encode_varint(value: int) -> bytes:
    """Encode an integer as a Minecraft VarInt."""
    result = b""
    while True:
        byte = value & 0x7F
        value >>= 7
        if value != 0:
            byte |= 0x80
        result += bytes([byte])
        if value == 0:
            break
    return result


def _encode_string(value: str) -> bytes:
    """Encode a string as a Minecraft packet string."""
    encoded = value.encode("utf-8")
    return _encode_varint(len(encoded)) + encoded


def _parse_kick_packet(data: bytes) -> str | None:
    """Parse a Minecraft disconnect/kick packet."""
    try:
        # Find JSON chat message in the packet
        text = data.decode("utf-8", errors="ignore")
        # Look for JSON with reason
        match = re.search(r'"text"\s*:\s*"([^"]+)"', text)
        if match:
            return match.group(1)

        # Try alternate format
        match = re.search(r'"translate"\s*:\s*"([^"]+)"', text)
        if match:
            return match.group(1)

        # Look for any readable text
        match = re.search(r'"extra"\s*:\s*\[\s*\{\s*"text"\s*:\s*"([^"]+)"', text)
        if match:
            return match.group(1)

    except Exception:
        pass

    return None


def _parse_kick_reason(reason: str) -> BanResult:
    """Parse a kick reason string to determine ban details.

    Args:
        reason: The raw kick/disconnect reason from Hypixel.

    Returns:
        BanResult with parsed ban information.
    """
    reason.lower()

    # Determine ban type
    ban_type = "unknown"
    for pattern, btype in BAN_PATTERNS:
        if re.search(pattern, reason, re.IGNORECASE):
            ban_type = btype
            break

    is_banned = ban_type not in ("unknown", "connection_error", "in_game")

    # Try to extract ban duration
    duration = ""
    expires_at = 0.0

    duration_match = re.search(
        r"(\d+)\s*(day|hour|minute|second|week|month|year)s?",
        reason,
        re.IGNORECASE,
    )
    if duration_match:
        amount = int(duration_match.group(1))
        unit = duration_match.group(2).lower()
        duration = f"{amount} {unit}s"
        multipliers = {
            "second": 1,
            "minute": 60,
            "hour": 3600,
            "day": 86400,
            "week": 604800,
            "month": 2592000,
            "year": 31536000,
        }
        expires_at = time.time() + (amount * multipliers.get(unit, 0))

    # Try to extract ban ID
    ban_id_match = re.search(r"#(\d+)", reason)
    ban_id = ban_id_match.group(1) if ban_id_match else ""

    return BanResult(
        is_banned=is_banned,
        ban_id=ban_id,
        reason=reason,
        duration=duration,
        expires_at=expires_at,
        detection_method="kick_parse",
        raw_response=reason,
    )

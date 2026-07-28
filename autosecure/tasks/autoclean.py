"""Temp file cleanup background task."""

from __future__ import annotations

import logging
import time
from pathlib import Path

log = logging.getLogger(__name__)

TEMP_DIR = Path("temp")
MAX_AGE_SECONDS = 3600  # 1 hour


async def clean_temp_files() -> None:
    """Delete temporary files older than the maximum age.

    Runs periodically (default every hour) to remove stale temp images,
    generated cards, and other temporary files.
    """
    if not TEMP_DIR.exists():
        return

    now = time.time()
    cleaned = 0

    try:
        for file_path in TEMP_DIR.rglob("*"):
            if file_path.is_file():
                try:
                    age = now - file_path.stat().st_mtime
                    if age > MAX_AGE_SECONDS:
                        file_path.unlink()
                        cleaned += 1
                except OSError as exc:
                    log.debug("Could not delete %s: %s", file_path, exc)

        if cleaned > 0:
            log.info("Cleaned %d temp files", cleaned)
    except Exception as exc:
        log.error("Temp file cleanup failed: %s", exc)

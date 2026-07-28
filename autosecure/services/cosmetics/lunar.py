"""LabyMod cosmetics service."""

from __future__ import annotations

import httpx

from autosecure.core.logging import get_logger

log = get_logger("cosmetics.laby")

LABY_API_URL = "https://lfr.littleskin.cn/api/mc-skin-renderer/v2/laby-mod"


async def get_cosmetics(uuid: str) -> dict:
    """Fetch LabyMod cosmetics for a Minecraft UUID.

    Args:
        uuid: Minecraft UUID (with or without dashes).

    Returns:
        Dictionary with LabyMod cosmetics data.
    """
    clean_uuid = uuid.replace("-", "")
    log.info("laby.get_cosmetics", uuid=clean_uuid)

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(
                f"{LABY_API_URL}/{clean_uuid}",
                headers={"Accept": "application/json"},
            )

            if response.status_code == 200:
                data = response.json()
                log.info(
                    "laby.get_cosmetics.success",
                    uuid=clean_uuid,
                    has_data=bool(data),
                )
                return data

            log.warning(
                "laby.get_cosmetics.failed",
                uuid=clean_uuid,
                status=response.status_code,
            )
            return {}

    except httpx.HTTPError as e:
        log.error("laby.get_cosmetics.http_error", uuid=clean_uuid, error=str(e))
        return {}
    except Exception as e:
        log.error("laby.get_cosmetics.error", uuid=clean_uuid, error=str(e))
        return {}

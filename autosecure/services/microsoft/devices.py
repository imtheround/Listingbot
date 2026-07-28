"""Microsoft/Xbox device management operations."""

from __future__ import annotations

import structlog

from autosecure.services.microsoft._http import MicrosoftHTTPClient

log = structlog.get_logger("microsoft.devices")

DEVICES_API = "https://device.xboxlive.com/v2.0/device/deletedevices"


class MicrosoftDevices:
    """Manages Xbox device registrations for an account.

    Provides methods to list, remove, and bulk-remove devices.
    """

    def __init__(self, proxy: str | None = None) -> None:
        """Initialize the device manager.

        Args:
            proxy: Optional proxy URL for requests.
        """
        self.proxy = proxy

    def _auth_headers(self, access_token: str) -> dict[str, str]:
        """Build authorization headers for Xbox Live APIs.

        Args:
            access_token: The Xbox Live access token.

        Returns:
            Headers dict.
        """
        return {
            "Authorization": f"XBL3.0 x={access_token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    async def get_devices(self, access_token: str) -> list[dict]:
        """Retrieve all devices registered to the account.

        Args:
            access_token: The Xbox Live access token.

        Returns:
            A list of device dictionaries with id, name, and type.
        """
        headers = self._auth_headers(access_token)
        async with MicrosoftHTTPClient(proxy=self.proxy) as client:
            try:
                response = await client.get(
                    "https://device.xboxlive.com/v2.0/device",
                    headers=headers,
                )
                data = response.json()
                devices = data.get("Results", data.get("results", []))
                log.info("devices_fetched", count=len(devices))
                return devices
            except Exception as exc:
                log.error("devices_fetch_failed", error=str(exc))
                return []

    async def remove_device(self, access_token: str, device_id: str) -> bool:
        """Remove a single device registration.

        Args:
            access_token: The Xbox Live access token.
            device_id: The ID of the device to remove.

        Returns:
            True if the device was removed successfully.
        """
        headers = self._auth_headers(access_token)
        async with MicrosoftHTTPClient(proxy=self.proxy) as client:
            try:
                response = await client.post(
                    DEVICES_API,
                    json={"DeviceIds": [device_id]},
                    headers=headers,
                )
                log.info("device_removed", device_id=device_id, status=response.status_code)
                return response.status_code == 200
            except Exception as exc:
                log.error("device_remove_failed", device_id=device_id, error=str(exc))
                return False

    async def remove_all_devices(self, access_token: str) -> int:
        """Remove all devices registered to the account.

        Args:
            access_token: The Xbox Live access token.

        Returns:
            The number of devices successfully removed.
        """
        devices = await self.get_devices(access_token)
        if not devices:
            return 0

        device_ids = [d.get("id", d.get("DeviceId", "")) for d in devices]
        device_ids = [did for did in device_ids if did]

        if not device_ids:
            return 0

        headers = self._auth_headers(access_token)
        async with MicrosoftHTTPClient(proxy=self.proxy) as client:
            try:
                response = await client.post(
                    DEVICES_API,
                    json={"DeviceIds": device_ids},
                    headers=headers,
                )
                count = len(device_ids) if response.status_code == 200 else 0
                log.info("all_devices_removed", count=count)
                return count
            except Exception as exc:
                log.error("bulk_device_remove_failed", error=str(exc))
                return 0

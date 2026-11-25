"""Coordinator for cached Teslita vehicle data."""

from __future__ import annotations

import asyncio
import logging
from datetime import timedelta
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .api import TeslitaApi, TeslitaApiError
from .const import DOMAIN


class TeslitaCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Fetch each vehicle's latest cached telemetry once per update cycle."""

    def __init__(
        self, hass: HomeAssistant, api: TeslitaApi, scan_interval: int
    ) -> None:
        self.api = api
        self.vehicles: list[dict[str, Any]] = []
        super().__init__(
            hass,
            logger=logging.getLogger(__name__),
            name=DOMAIN,
            update_interval=timedelta(seconds=scan_interval),
        )

    async def _async_update_data(self) -> dict[str, Any]:
        try:
            if not self.vehicles:
                self.vehicles = await self.api.get_vehicles()
            results = await asyncio.gather(
                *(
                    asyncio.gather(
                        self.api.get_vehicle_state(vehicle["vin"]),
                        self.api.get_vehicle_location(vehicle["vin"]),
                        self.api.get_pack_health(vehicle["vin"]),
                    )
                    for vehicle in self.vehicles
                )
            )
        except TeslitaApiError as err:
            raise UpdateFailed(str(err)) from err
        return {
            vehicle["vin"]: {
                "vehicle": vehicle,
                "state": result[0],
                "location": result[1],
                "pack_health": result[2],
            }
            for vehicle, result in zip(self.vehicles, results, strict=True)
            if vehicle.get("vin")
        }

"""Device trackers for Teslita vehicle locations."""

from __future__ import annotations

from homeassistant.components.device_tracker import SourceType, TrackerEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import TeslitaCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up location entities."""
    coordinator: TeslitaCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(TeslitaTracker(coordinator, vin) for vin in coordinator.data)


class TeslitaTracker(CoordinatorEntity[TeslitaCoordinator], TrackerEntity):
    """Expose the most recently received vehicle coordinates."""

    _attr_has_entity_name = True
    _attr_name = "Standort"
    _attr_source_type = SourceType.GPS

    def __init__(self, coordinator: TeslitaCoordinator, vin: str) -> None:
        super().__init__(coordinator)
        self._vin = vin
        vehicle = coordinator.data[vin]["vehicle"]
        name = vehicle.get("custom_name") or vehicle.get("display_name") or vehicle.get("model") or vin
        self._attr_unique_id = f"{vin}_location"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, vin)},
            name=name,
            manufacturer="Tesla",
            model=vehicle.get("model"),
            serial_number=vin,
        )

    @property
    def latitude(self) -> float | None:
        """Return the last known latitude."""
        location = self.coordinator.data.get(self._vin, {}).get("location") or {}
        return location.get("latitude")

    @property
    def longitude(self) -> float | None:
        """Return the last known longitude."""
        location = self.coordinator.data.get(self._vin, {}).get("location") or {}
        return location.get("longitude")

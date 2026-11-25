"""Binary sensors for Teslita vehicle state."""

from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
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
    """Set up movement sensors."""
    coordinator: TeslitaCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(TeslitaDrivingSensor(coordinator, vin) for vin in coordinator.data)


class TeslitaDrivingSensor(
    CoordinatorEntity[TeslitaCoordinator], BinarySensorEntity
):
    """Indicate whether Teslita reports a vehicle as driving or moving."""

    _attr_has_entity_name = True
    _attr_name = "Fahrzeug bewegt sich"
    _attr_device_class = BinarySensorDeviceClass.MOVING

    def __init__(self, coordinator: TeslitaCoordinator, vin: str) -> None:
        """Initialize the movement sensor."""
        super().__init__(coordinator)
        self._vin = vin
        vehicle = coordinator.data[vin]["vehicle"]
        name = vehicle.get("custom_name") or vehicle.get("display_name") or vehicle.get("model") or vin
        self._attr_unique_id = f"{vin}_driving"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, vin)},
            name=name,
            manufacturer="Tesla",
            model=vehicle.get("model"),
            serial_number=vin,
        )

    @property
    def is_on(self) -> bool | None:
        """Return Teslita's cached movement flag, when available."""
        location = self.coordinator.data.get(self._vin, {}).get("location") or {}
        return location.get("driving")

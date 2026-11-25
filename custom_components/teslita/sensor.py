"""Sensors for Teslita vehicle state."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory, PERCENTAGE, UnitOfEnergy, UnitOfLength
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import TeslitaCoordinator


@dataclass(frozen=True, kw_only=True)
class TeslitaSensorDescription(SensorEntityDescription):
    """Describe a sensor and its field in a cached API response."""

    value_key: str
    data_source: str = "state"


SENSORS = (
    TeslitaSensorDescription(key="battery_level", name="Batteriestand", value_key="battery_level", native_unit_of_measurement=PERCENTAGE),
    TeslitaSensorDescription(key="charging_state", name="Ladestatus", value_key="charging_state"),
    TeslitaSensorDescription(key="charge_limit_soc", name="Ladelimit", value_key="charge_limit_soc", native_unit_of_measurement=PERCENTAGE),
    TeslitaSensorDescription(key="energy_remaining_kwh", name="Restenergie", value_key="energy_remaining_kwh", native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR),
    TeslitaSensorDescription(key="rated_range_km", name="Reichweite", value_key="rated_range_km", native_unit_of_measurement=UnitOfLength.KILOMETERS),
    TeslitaSensorDescription(key="odometer_km", name="Kilometerstand", value_key="odometer_km", native_unit_of_measurement=UnitOfLength.KILOMETERS),
    TeslitaSensorDescription(key="last_signal_at", name="Letztes Signal", value_key="last_signal_at", device_class=SensorDeviceClass.TIMESTAMP, entity_category=EntityCategory.DIAGNOSTIC),
    TeslitaSensorDescription(key="tpms_front_left", name="Reifendruck vorne links", value_key="front_left", data_source="pack_health", native_unit_of_measurement="bar", device_class=SensorDeviceClass.PRESSURE),
    TeslitaSensorDescription(key="tpms_front_right", name="Reifendruck vorne rechts", value_key="front_right", data_source="pack_health", native_unit_of_measurement="bar", device_class=SensorDeviceClass.PRESSURE),
    TeslitaSensorDescription(key="tpms_rear_left", name="Reifendruck hinten links", value_key="rear_left", data_source="pack_health", native_unit_of_measurement="bar", device_class=SensorDeviceClass.PRESSURE),
    TeslitaSensorDescription(key="tpms_rear_right", name="Reifendruck hinten rechts", value_key="rear_right", data_source="pack_health", native_unit_of_measurement="bar", device_class=SensorDeviceClass.PRESSURE),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up vehicle sensors."""
    coordinator: TeslitaCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        TeslitaSensor(coordinator, vin, description)
        for vin in coordinator.data
        for description in SENSORS
    )


class TeslitaSensor(CoordinatorEntity[TeslitaCoordinator], SensorEntity):
    """Expose a field from Teslita's read-only cached state."""

    entity_description: TeslitaSensorDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: TeslitaCoordinator,
        vin: str,
        description: TeslitaSensorDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._vin = vin
        vehicle = coordinator.data[vin]["vehicle"]
        self._name = vehicle.get("custom_name") or vehicle.get("display_name") or vehicle.get("model") or vin
        self._attr_unique_id = f"{vin}_{description.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, vin)},
            name=self._name,
            manufacturer="Tesla",
            model=vehicle.get("model"),
            serial_number=vin,
        )

    @property
    def name(self) -> str:
        """Return sensor name with vehicle name as device name."""
        return self.entity_description.name

    @property
    def native_value(self) -> Any:
        """Return the latest cached value."""
        vehicle_data = self.coordinator.data.get(self._vin, {})
        if self.entity_description.data_source == "pack_health":
            tpms_bar = (vehicle_data.get("pack_health") or {}).get("tpms_bar") or {}
            return tpms_bar.get(self.entity_description.value_key)
        value = (vehicle_data.get("state") or {}).get(self.entity_description.value_key)
        if self.entity_description.device_class == SensorDeviceClass.TIMESTAMP and isinstance(value, str):
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        return value

"""Teslita Home Assistant integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import TeslitaApi, TeslitaApiError
from .const import (
    CONF_API_KEY,
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    PLATFORMS,
)
from .coordinator import TeslitaCoordinator


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Teslita from a config entry."""
    api = TeslitaApi(
        async_get_clientsession(hass), entry.data[CONF_API_KEY]
    )
    coordinator = TeslitaCoordinator(
        hass,
        api,
        entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
    )
    await coordinator.async_config_entry_first_refresh()
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload Teslita platforms."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok


async def async_remove_config_entry_device(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    device_entry: dr.DeviceEntry,
) -> bool:
    """Allow removing vehicles that are no longer connected to Teslita."""
    vins = {
        identifier
        for domain, identifier in device_entry.identifiers
        if domain == DOMAIN
    }
    if len(vins) != 1:
        return False

    api = TeslitaApi(
        async_get_clientsession(hass), config_entry.data[CONF_API_KEY]
    )
    try:
        vehicles = await api.get_vehicles()
    except TeslitaApiError:  # Keep the device if its status cannot be confirmed.
        return False
    active_vins = {vehicle["vin"] for vehicle in vehicles}
    return not vins.intersection(active_vins)

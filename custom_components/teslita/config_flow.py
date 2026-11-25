"""Config flow for Teslita."""

from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.config_entries import ConfigEntry, OptionsFlowWithReload
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import TeslitaApi, TeslitaApiError
from .const import (
    CONF_API_KEY,
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    MAX_SCAN_INTERVAL,
    MIN_SCAN_INTERVAL,
)


class TeslitaConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Set up Teslita using a read-scoped API key."""

    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> TeslitaOptionsFlow:
        """Create the options flow for Teslita."""
        return TeslitaOptionsFlow()

    async def async_step_user(self, user_input=None):
        errors: dict[str, str] = {}
        if user_input is not None:
            api = TeslitaApi(
                async_get_clientsession(self.hass), user_input[CONF_API_KEY].strip()
            )
            try:
                account = await api.get_me()
                vehicles = await api.get_vehicles()
            except TeslitaApiError:
                errors["base"] = "cannot_connect"
            else:
                scopes = account.get("key", {}).get("scopes", [])
                if "read" not in scopes:
                    errors["base"] = "invalid_auth"
                elif not vehicles:
                    errors["base"] = "no_vehicles"
                else:
                    await self.async_set_unique_id(str(account.get("user", {}).get("id")))
                    self._abort_if_unique_id_configured()
                    return self.async_create_entry(
                        title=account.get("user", {}).get("display_name") or "Teslita",
                        data={CONF_API_KEY: user_input[CONF_API_KEY].strip()},
                    )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({vol.Required(CONF_API_KEY): str}),
            errors=errors,
        )


class TeslitaOptionsFlow(OptionsFlowWithReload):
    """Manage Teslita polling options."""

    async def async_step_init(self, user_input=None):
        """Configure the update interval."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_SCAN_INTERVAL,
                        default=self.config_entry.options.get(
                            CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
                        ),
                    ): vol.All(
                        vol.Coerce(int),
                        vol.Range(min=MIN_SCAN_INTERVAL, max=MAX_SCAN_INTERVAL),
                    )
                }
            ),
        )

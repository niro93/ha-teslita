"""Small read-only client for the Teslita API."""

from __future__ import annotations

import asyncio
from typing import Any

import aiohttp

from .const import BASE_URL

ERROR_MESSAGES = {
    "missing_auth": "Der API-Schlüssel fehlt.",
    "invalid_auth": "Der API-Schlüssel ist ungültig oder wurde widerrufen.",
    "forbidden": "Der API-Schlüssel hat keine ausreichende Berechtigung.",
    "not_found": "Die angeforderten Teslita-Daten wurden nicht gefunden.",
    "bad_request": "Die Anfrage an Teslita ist ungültig.",
    "rate_limited": "Das Teslita-Anfragelimit wurde erreicht.",
    "tesla_not_connected": "Mit diesem Teslita-Konto ist kein Tesla-Konto verbunden.",
    "upstream_error": "Der Tesla-Dienst ist derzeit nicht erreichbar.",
    "internal_error": "Bei Teslita ist ein interner Fehler aufgetreten.",
}


class TeslitaApiError(Exception):
    """Error returned by the Teslita API."""


class TeslitaApi:
    """Read-only Teslita API client."""

    def __init__(self, session: aiohttp.ClientSession, api_key: str) -> None:
        self._session = session
        self._api_key = api_key

    async def _get(self, path: str) -> dict[str, Any]:
        try:
            async with self._session.get(
                f"{BASE_URL}{path}",
                headers={"Authorization": f"Bearer {self._api_key}"},
                timeout=aiohttp.ClientTimeout(total=20),
            ) as response:
                payload = await response.json(content_type=None)
                if response.status >= 400:
                    error = payload.get("error", {}) if isinstance(payload, dict) else {}
                    code = error.get("code")
                    message = ERROR_MESSAGES.get(
                        code, f"Teslita hat einen HTTP-Fehler {response.status} gemeldet."
                    )
                    raise TeslitaApiError(message)
                if not isinstance(payload, dict):
                    raise TeslitaApiError("Teslita hat eine unerwartete Antwort gesendet.")
                return payload
        except asyncio.TimeoutError as err:
            raise TeslitaApiError("Zeitüberschreitung bei der Anfrage an Teslita.") from err
        except aiohttp.ClientError as err:
            raise TeslitaApiError("Verbindung zur Teslita-API fehlgeschlagen.") from err

    async def get_me(self) -> dict[str, Any]:
        """Validate the key and return account metadata."""
        return await self._get("/me")

    async def get_vehicles(self) -> list[dict[str, Any]]:
        """Return currently connected vehicles, excluding archived vehicles."""
        response = await self._get("/vehicles")
        data = response.get("data", [])
        if not isinstance(data, list):
            return []
        return [
            vehicle
            for vehicle in data
            if isinstance(vehicle, dict)
            and vehicle.get("vin")
            and not vehicle.get("disconnected_at")
        ]

    async def get_vehicle_state(self, vin: str) -> dict[str, Any] | None:
        """Return only the requested vehicle values from cached telemetry."""
        response = await self._get(f"/vehicles/{vin}/state")
        data = response.get("data")
        if not isinstance(data, dict):
            return None
        return {
            key: data.get(key)
            for key in (
                "battery_level",
                "charging_state",
                "charge_limit_soc",
                "energy_remaining_kwh",
                "rated_range_km",
                "odometer_km",
                "last_signal_at",
            )
        }

    async def get_vehicle_location(self, vin: str) -> dict[str, Any] | None:
        """Return only position and movement state from the location response."""
        response = await self._get(f"/vehicles/{vin}/location")
        data = response.get("data")
        if not isinstance(data, dict):
            return None
        return {
            key: data.get(key) for key in ("latitude", "longitude", "driving")
        }

    async def get_pack_health(self, vin: str) -> dict[str, Any] | None:
        """Return only tire pressure from the latest stored pack-health sample."""
        response = await self._get(f"/vehicles/{vin}/pack-health")
        data = response.get("data")
        if not isinstance(data, dict):
            return None
        return {"tpms_bar": data.get("tpms_bar")}

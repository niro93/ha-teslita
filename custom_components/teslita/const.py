"""Constants for the Teslita integration."""

DOMAIN = "teslita"
BASE_URL = "https://api.teslita.com/v1"
CONF_API_KEY = "api_key"
CONF_SCAN_INTERVAL = "scan_interval"
PLATFORMS = ("sensor", "binary_sensor", "device_tracker")

# Teslita's documented default is 120 requests per minute per API key.
DEFAULT_SCAN_INTERVAL = 300
MIN_SCAN_INTERVAL = 60
MAX_SCAN_INTERVAL = 3600

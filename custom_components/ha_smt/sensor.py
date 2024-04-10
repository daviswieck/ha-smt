import asyncio
import logging
from datetime import timedelta
import aiohttp
import json
from homeassistant.helpers.entity import Entity

DOMAIN = "ha_smt"

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(minutes=60)

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the HA-SMT sensor."""
    # Register the sensor with configuration from the config flow
    async_add_entities([HaSmtSensor(hass)], True)

class HaSmtSensor(Entity):
    """Representation of a HA-SMT sensor."""

    def __init__(self, hass):
        """Initialize the sensor."""
        self._hass = hass
        self._state = None
        self._unit_of_measurement = 'kWh'

    @property
    def name(self):
        """Return the name of the sensor."""
        return 'HA-SMT'

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement of the sensor."""
        return self._unit_of_measurement

    async def async_update(self):
        """Update the sensor data."""
        # Retrieve configuration data from Home Assistant's data entry
        config_entry = next(
            entry for entry in self._hass.config_entries.async_entries("ha_smt")
        )
        username = config_entry.data.get("username")
        password = config_entry.data.get("password")
        esiid = config_entry.data.get("esiid")
        meter_number = config_entry.data.get("meter_number")

        auth_data = {
            "username": username,
            "password": password,
            "rememberMe": "true"
        }
        meter_data = {
            "ESIID": esiid,
            "MeterNumber": meter_number
        }

        headers = {
            "accept": "application/json, text/plain, */*",
            "accept-language": "en-US,en;q=0.9",
            "cache-control": "no-cache",
            "content-type": "application/json",
            "origin": "https://www.smartmetertexas.com",
            "pragma": "no-cache",
            "referer": "https://www.smartmetertexas.com/home",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        }

        async with aiohttp.ClientSession() as session:
            # Step 1: Authenticate
            async with session.post("https://www.smartmetertexas.com/commonapi/user/authenticate", json=auth_data, headers=headers) as response:
                auth_result = await response.json()
                token = auth_result.get('token')

                if not token:
                    _LOGGER.error("Authentication failed")
                    return

                # Step 2: Request on-demand read
                headers["authorization"] = f"Bearer {token}"
                async with session.post("https://www.smartmetertexas.com/api/ondemandread", json=meter_data, headers=headers) as response:
                    odr_result = await response.json()
                    odr_status = odr_result.get('data', {}).get('odrstatus')

                    # Step 3: Poll for latest on-demand read
                    while odr_status != 'COMPLETED':
                        await asyncio.sleep(30)
                        async with session.post("https://www.smartmetertexas.com/api/usage/latestodrread", json=meter_data, headers=headers) as fetch_response:
                            fetch_odr_result = await fetch_response.json()
                            odr_status = fetch_odr_result.get('data', {}).get('odrstatus')

                    self._state = fetch_odr_result.get('data', {}).get('odrread')
                    _LOGGER.debug(f"HA-SMT Reading Updated: {self._state}")

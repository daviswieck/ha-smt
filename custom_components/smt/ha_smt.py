"""Integration with SmartMeterTexas."""
import logging
import asyncio

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.helpers.aiohttp_client import async_get_clientsession

_LOGGER = logging.getLogger(__name__)

DOMAIN = "smt"

CONFIG_SCHEMA = vol.Schema({DOMAIN: vol.Schema({})}, extra=vol.ALLOW_EXTRA)

async def async_setup(hass, config):
    """Set up the SmartMeterTexas component."""
    return True

async def async_request_meter_reading(hass, meter_data):
    """Request meter reading from SmartMeterTexas."""
    session = async_get_clientsession(hass)
    headers = {
        "accept": "application/json, text/plain, */*",
        "content-type": "application/json",
        "user-agent": "YOUR_USER_AGENT_STRING",
    }
    url = "https://www.smartmetertexas.com/api/ondemandread"
    try:
        response = await session.post(url, json=meter_data, headers=headers)
        response_data = await response.json()
        return response_data
    except Exception as e:
        _LOGGER.error(f"Error requesting meter reading: {e}")
        return None

async def async_handle_meter_reading(hass, meter_data):
    """Handle the meter reading."""
    response_data = await async_request_meter_reading(hass, meter_data)
    if response_data and "data" in response_data and "odrstatus" in response_data["data"]:
        odr_status = response_data["data"]["odrstatus"]
        if odr_status == "COMPLETED":
            odr_reading = response_data["data"]["odrread"]
            _LOGGER.info(f"Received meter reading: {odr_reading}")
            # You can further process or use the meter reading here
        else:
            _LOGGER.warning(f"Meter reading status is not COMPLETED: {odr_status}")
    else:
        _LOGGER.error("Invalid response received for meter reading request")

async def async_service_handler(call):
    """Handle service calls."""
    meter_data = call.data.get("meter_data")
    if meter_data:
        await async_handle_meter_reading(call.data["meter_data"])

async def async_setup(hass, config):
    """Set up the SmartMeterTexas component."""
    hass.services.async_register(DOMAIN, "request_meter_reading", async_service_handler)
    return True

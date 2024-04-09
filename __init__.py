"""The SmartMeterTexas integration."""
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

DOMAIN = "smt"

async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the SmartMeterTexas component."""
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up SmartMeterTexas from a config entry."""
    # Add setup code here, if necessary
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    # Add cleanup code here, if necessary
    return True


"""The HA-SMT integration."""

import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)

DOMAIN = "ha_smt"

async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the HA-SMT integration."""
    # If configuration is present in YAML, initiate setup
    if DOMAIN in config:
        yaml_config = config[DOMAIN]
        username = yaml_config.get("username")
        password = yaml_config.get("password")
        esiid = yaml_config.get("esiid")
        meter_number = yaml_config.get("meter_number")

        if all(val is not None for val in [username, password, esiid, meter_number]):
            hass.async_create_task(
                hass.config_entries.flow.async_init(
                    DOMAIN,
                    context={"source": "yaml"},
                    data={"username": username, "password": password, "esiid": esiid, "meter_number": meter_number},
                )
            )

    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up HA-SMT from a config entry."""
    # Forward the setup to the sensor platform
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, "sensor")
    )
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    # Unload the sensor platform
    return await hass.config_entries.async_forward_entry_unload(entry, "sensor")

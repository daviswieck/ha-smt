from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

DOMAIN = "ha_smt"

async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the Smart Meter Texas integration."""
    # No configuration necessary for this type of integration
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up Smart Meter Texas from a config entry."""
    # Perform setup for the configured entry (e.g., create entities)
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, "sensor")
    )
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    # Perform cleanup when an entry is unloaded (e.g., unload entities)
    return True

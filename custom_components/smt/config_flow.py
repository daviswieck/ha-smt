import voluptuous as vol
from homeassistant import config_entries

DOMAIN = "ha_smt"

class SmartMeterTexasConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):

    async def async_step_user(self, user_input=None):
        """Handle a flow initiated by the user."""
        if user_input is not None:
            # Validate user input and create a config entry
            return self.async_create_entry(title="Smart Meter Texas", data=user_input)

        # Show the form to the user
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("username"): str,
                vol.Required("password"): str,
                vol.Required("esiid"): str,
                vol.Required("meter_number"): str,
            })
        )

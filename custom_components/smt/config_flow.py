import voluptuous as vol
from homeassistant import config_entries

DOMAIN = "smt"

class HaSmtConfigFlow(config_entries.ConfigFlow):
  """Config flow for HA-SMT."""

  async def async_step_user(self, user_input=None):
    """Handle the initial step."""
    if user_input is not None:
      # Validate user input
      username = user_input.get("username")
      password = user_input.get("password")
      esiid = user_input.get("esiid")
      meter_number = user_input.get("meter_number")

      if username and password and esiid and meter_number:
        return self.async_create_entry(
          title="HA-SMT",
          data=user_input,
        )
      else:
        return self.async_show_form(
          step_id="user",
          errors={"base": "invalid_input"},
          data_schema=vol.Schema({
            vol.Required("username"): str,
            vol.Required("password"): str,
            vol.Required("esiid"): str,
            vol.Required("meter_number"): str,
          }),
        )

    # Show the initial form
    return self.async_show_form(
      step_id="user",
      data_schema=vol.Schema({
        vol.Required("username"): str,
        vol.Required("password"): str,
        vol.Required("esiid"): str,
        vol.Required("meter_number"): str,
      }),
    )
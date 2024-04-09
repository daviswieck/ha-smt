"""Platform for SmartMeterTexas."""
import asyncio
import logging
import json
import http.client

from homeassistant.const import CONF_USERNAME, CONF_PASSWORD, CONF_ESIID, CONF_METER_NUMBER
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import voluptuous as vol

DOMAIN = "ha_smt"

# Config schema for configuration flow
CONFIG_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_USERNAME): str,
        vol.Required(CONF_PASSWORD): str,
        vol.Required(CONF_ESIID): str,
        vol.Required(CONF_METER_NUMBER): str,
    }
)

async def async_setup(hass, config):
    """Set up the ha_smt component."""
    return True

async def async_setup_entry(hass, config_entry):
    """Set up ha_smt from a config entry."""
    username = config_entry.data[CONF_USERNAME]
    password = config_entry.data[CONF_PASSWORD]
    esiid = config_entry.data[CONF_ESIID]
    meter_number = config_entry.data[CONF_METER_NUMBER]

    # Your setup code here to authenticate and retrieve data
    await authenticate_and_retrieve_data(hass, username, password, esiid, meter_number)

    return True

async def async_unload_entry(hass, config_entry):
    """Unload a config entry."""
    # Perform cleanup tasks when a config entry is unloaded
    return True

async def authenticate_and_retrieve_data(hass, username, password, esiid, meter_number):
    """Authenticate and retrieve data from SmartMeterTexas."""
    # Define connection and headers
    conn = http.client.HTTPSConnection("www.smartmetertexas.com")
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

    auth_data = {
        "username": username,
        "password": password,
        "rememberMe": "true",
    }

    meter_data = {
        "ESIID": esiid,
        "MeterNumber": meter_number,
    }

    try:
        # Step 1: Attempt to authenticate and retrieve bearer token for session
        conn.request("POST", "/commonapi/user/authenticate", json.dumps(auth_data), headers)
        response = conn.getresponse()

        if response.status != 200:
            raise Exception(f"Authentication failed with status code: {response.status}")

        auth_result = json.loads(response.read().decode())

        if "token" not in auth_result:
            raise Exception("No token returned in authorization request")

        token = auth_result["token"]
        headers["authorization"] = f"Bearer {token}"

        # Step 2: Request on-demand read of meter
        conn.request("POST", "/api/ondemandread", json.dumps(meter_data), headers)
        odr_response = conn.getresponse()

        if odr_response.status != 200:
            raise Exception(f"Failed to request on-demand read with status code: {odr_response.status}")

        odr_result = json.loads(odr_response.read().decode())["data"]

        if odr_result["statusCode"] == "5031":
            # Too many attempted reads in 1 hour, log and move on
            logging.warning(odr_result["statusReason"])
        elif odr_result["statusCode"] != "0":
            raise Exception(f"Error requesting on-demand read: {odr_result['statusReason']}")

        # Step 3: Poll the latest on-demand read endpoint until a valid reading is returned
        odr_status = "NOT_RECEIVED"
        while odr_status != "COMPLETED":
            await asyncio.sleep(30)

            conn.request("POST", "/api/usage/latestodrread", json.dumps(meter_data), headers)
            fetch_odr_response = conn.getresponse()

            if fetch_odr_response.status != 200:
                raise Exception(f"Failed to fetch on-demand read with status code: {fetch_odr_response.status}")

            fetch_odr_result = json.loads(fetch_odr_response.read().decode())["data"]
            odr_status = fetch_odr_result["odrstatus"]

            if odr_status == "COMPLETED":
                odr_reading = fetch_odr_result["odrread"]
                logging.info(f"Received on-demand reading: {odr_reading}")
            elif odr_status != "PENDING":
                raise Exception("Could not retrieve the meter reading")

    except Exception as e:
        logging.error(f"Error during data retrieval: {e}")
    finally:
        conn.close()

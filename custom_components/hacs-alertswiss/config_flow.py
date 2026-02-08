import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_LATITUDE, CONF_LONGITUDE
from homeassistant.helpers import config_validation as cv
from .const import DOMAIN, CONF_RADIUS, DEFAULT_RADIUS

class AlertSwissConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    async def async_step_user(self, user_input=None):
        """Erstes Formular im Integrations-UI"""
        if user_input is None:
            # Formular anzeigen
            return self.async_show_form(
                step_id="user",
                data_schema=vol.Schema({
                    vol.Required(CONF_LATITUDE, default=self.hass.config.latitude): cv.latitude,
                    vol.Required(CONF_LONGITUDE, default=self.hass.config.longitude): cv.longitude,
                    vol.Required(CONF_RADIUS, default=DEFAULT_RADIUS): vol.Coerce(float),
                })
            )

        # Eingaben speichern und Integration anlegen
        return self.async_create_entry(
            title="AlertSwiss",
            data={
                CONF_LATITUDE: user_input[CONF_LATITUDE],
                CONF_LONGITUDE: user_input[CONF_LONGITUDE],
                CONF_RADIUS: user_input[CONF_RADIUS],
            }
        )

    async def async_step_import(self, import_config):
        """Import aus configuration.yaml, falls gewünscht"""
        return await self.async_step_user(import_config)
class AlertSwissOptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Optionen-Formular zum Anpassen des Radius"""
        if user_input is None:
            current = self.config_entry.options.get(CONF_RADIUS,
                                                    self.config_entry.data[CONF_RADIUS])
            return self.async_show_form(
                step_id="init",
                data_schema=vol.Schema({
                    vol.Required(CONF_RADIUS, default=current): vol.Coerce(float),
                })
            )

        # Options speichern
        return self.async_create_entry(
            title="",
            data={CONF_RADIUS: user_input[CONF_RADIUS]}
        )

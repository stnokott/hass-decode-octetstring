"""
Converts Octet String values to plain string
"""
import urllib.error

import logging
from typing import Optional

import voluptuous as vol

from homeassistant.components.sensor import PLATFORM_SCHEMA, SensorEntity
from homeassistant.const import CONF_NAME, CONF_ENTITY_ID, EVENT_STATE_CHANGED
import homeassistant.helpers.config_validation as cv
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers.entity_platform import AddEntitiesCallback

_LOGGER = logging.getLogger(__name__)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_NAME): cv.string,
        vol.Required(CONF_ENTITY_ID): cv.string,
    }
)


def setup_platform(
        hass: HomeAssistant,
        config: ConfigType,
        add_entities: AddEntitiesCallback,
        discovery_info=None,
):
    _LOGGER.debug("Setting up sensor")

    name = config.get(CONF_NAME)
    entity_id = config.get(CONF_ENTITY_ID)

    try:
        sensor = OctetStringSensor(name, entity_id)
    except urllib.error.HTTPError as e:
        _LOGGER.error(e.reason)
        return False

    def handle_event(event):
        try:
            if event.data['entity_id'] == entity_id:
                sensor.entity_updated(event.data['new_state'].state)
        except KeyError:
            _LOGGER.warning(f"Can't find entity_id attr in {event.data}")

    hass.bus.listen(EVENT_STATE_CHANGED, handle_event)

    add_entities([sensor])


class OctetStringSensor(SensorEntity):
    _attr_should_poll = False

    def __init__(self, name, entity_id):
        self._name = name
        self._entity_id = entity_id
        self._available = True
        self._state = None

    def entity_updated(self, octet_string_value: Optional[str]) -> None:
        if octet_string_value is None:
            self._state = None
            self._available = False
        elif octet_string_value[:2] != "0x":
            _LOGGER.warning(
                f"State of entity {self._entity_id} does not start with '0x'!"
            )
            self._state = None
        try:
            int(octet_string_value[2:], 16)
        except ValueError:
            _LOGGER.warning(f"State of entity {self._entity_id} is not hexadecimal!")
        try:
            self._state = bytes.fromhex(octet_string_value[2:]).decode("utf-8")
        except ValueError as e:
            _LOGGER.error(
                f"Encountered error while parsing state of {self._entity_id}:\n{e}"
            )
        self._available = True
        self.async_write_ha_state()

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state

    @property
    def available(self) -> bool:
        return self._available

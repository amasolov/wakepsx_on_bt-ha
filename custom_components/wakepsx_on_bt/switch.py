"""Support for wakepsx on bt."""
import logging

import voluptuous as vol

from homeassistant.components.switch import (
    PLATFORM_SCHEMA as PARENT_PLATFORM_SCHEMA,
    SwitchEntity,
)
from .const import (
    CONF_ADAPTER,
    CONF_CONTROLER_BT_ADDRESS,
    CONF_PLAYSTATION_BT_ADDRESS,
    DOMAIN,
    SERVICE_SEND_MAGIC_PACKET,
    WOBTPSX_PREFIX,
)
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType


_LOGGER = logging.getLogger(__name__)


PLATFORM_SCHEMA = PARENT_PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_ADAPTER): cv.string,
        vol.Required(CONF_CONTROLER_BT_ADDRESS): cv.string,
        vol.Required(CONF_PLAYSTATION_BT_ADDRESS): cv.string,
        vol.Optional(CONF_NAME, default=""): cv.string,
    }
)


def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up a wake psx on bt switch."""
    adapter: str = config[CONF_ADAPTER]
    dsbt_address: str = config[CONF_CONTROLER_BT_ADDRESS]
    psxbt_address: str = config[CONF_PLAYSTATION_BT_ADDRESS]
    name: str = config[CONF_NAME]
    add_entities(
        [WOBTPSXSwitch(hass, adapter, psxbt_address, dsbt_address, name)],
        False,
    )


class WOBTPSXSwitch(SwitchEntity):
    """Representation of a wakepsx on bt switch."""

    _attr_assumed_state = True
    _attr_should_poll = False
    _attr_icon = "mdi:sony-playstation"

    def __init__(
        self,
        hass: HomeAssistant,
        adapter: str,
        psxbt_address: str,
        dsbt_address: str,
        name: str | None = None,
    ) -> None:
        """Initialize the wake PsX on BT switch."""
        self._hass = hass
        self._adapter = adapter
        self._psxbt_address = psxbt_address
        self._dsbt_address = dsbt_address
        self._state = False
        formatted_mac = dr.format_mac(self._psxbt_address)
        self._attr_name = name if name else WOBTPSX_PREFIX + formatted_mac
        self._attr_unique_id = WOBTPSX_PREFIX + formatted_mac

    @property
    def is_on(self) -> bool:
        """Return true if switch is on."""
        return self._state

    def turn_on(self, **kwargs) -> None:
        """Send BT wake packet to the PlayStation."""
        self._hass.services.call(
            DOMAIN,
            SERVICE_SEND_MAGIC_PACKET,
            {
                CONF_ADAPTER: self._adapter,
                CONF_CONTROLER_BT_ADDRESS: self._dsbt_address,
                CONF_PLAYSTATION_BT_ADDRESS: self._psxbt_address,
            },
        )

    def turn_off(self, **kwargs) -> None:
        """No-op: Bluetooth cannot turn off a PlayStation."""

"""Support for HUB-C2000PP alarm_control_panel."""
import logging
from typing import Any

from homeassistant.components.alarm_control_panel import (
    AlarmControlPanelEntity,
    AlarmControlPanelEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import HUBC2000PPDataUpdateCoordinator
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up Bolid sensor."""
    coordinator: HUBC2000PPDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    devices = coordinator.data["parts"]
    entities = []
    for device in devices:
        if device["desc"]:
            entities.append(AlarmControlPanelDevice(device, coordinator))

    async_add_entities(entities)


class AlarmControlPanelDevice(
    CoordinatorEntity[HUBC2000PPDataUpdateCoordinator], AlarmControlPanelEntity
):
    """Representation of an Bolid partition from HUB-C2000PP data."""

    def __init__(
        self, device: dict[str, Any], coordinator: HUBC2000PPDataUpdateCoordinator
    ) -> None:
        """Initialize the Bolid partition."""
        super().__init__(coordinator)

        device_name = f'Раздел {device["id"]}'
        device_uid = f'partition_{device["id"]}'

        self._attr_device_info = DeviceInfo(
            identifiers={
                (DOMAIN, device_uid),
            },
            manufacturer="Bolid",
            model="Раздел",
            name=device_name,
        )

        self._attr_name = device["desc"]
        self._attr_unique_id = device_uid
        self._attr_code_arm_required = False
        self._attr_code_format = None
        self._attr_supported_features = AlarmControlPanelEntityFeature.ARM_HOME

    async def async_alarm_disarm(self, code: str | None = None) -> None:
        """Disarm partition."""
        return

    async def async_alarm_arm_home(self, code: str | None = None) -> None:
        """Arm partition."""
        return

    async def async_alarm_trigger(self, code: str | None = None) -> None:
        """Partition alarm triggered."""
        return

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        device: dict[str, Any] | None = next(
            (
                device
                for device in self.coordinator.data["parts"]
                if f'partition_{device["id"]}' == self.unique_id
            ),
            None,
        )

        if device:
            state_code = int(device["stat"])
            self._attr_state = state_code

        super()._handle_coordinator_update()

    async def async_added_to_hass(self) -> None:
        """When entity is added to hass."""
        await super().async_added_to_hass()
        self._handle_coordinator_update()

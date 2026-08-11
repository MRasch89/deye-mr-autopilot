"""Switch platform for explicit physical-control arming."""

from __future__ import annotations

from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import DOMAIN
from .entity import DeyeMRAutopilotEntity

CONTROL_ARMED = SwitchEntityDescription(
    key="control_armed",
    translation_key="control_armed",
    icon="mdi:shield-lock",
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the control-arming switch."""
    async_add_entities([DeyeControlArmedSwitch(entry.runtime_data.coordinator)])


class DeyeControlArmedSwitch(DeyeMRAutopilotEntity, SwitchEntity):
    """Explicit arming switch; Phase 1 always refuses to arm."""

    entity_description = CONTROL_ARMED

    def __init__(self, coordinator) -> None:
        super().__init__(coordinator, CONTROL_ARMED.key)

    @property
    def is_on(self) -> bool:
        """Return whether physical control is armed."""
        return self.coordinator.config_entry.runtime_data.control_armed

    async def async_turn_on(self, **kwargs) -> None:
        """Refuse arming while only the mock adapter is available."""
        self.coordinator.config_entry.runtime_data.control_armed = False
        self.hass.bus.async_fire(
            f"{DOMAIN}_control_arm_blocked",
            {"reason": "physical_control_not_implemented"},
        )
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs) -> None:
        """Disarm physical control."""
        self.coordinator.config_entry.runtime_data.control_armed = False
        self.async_write_ha_state()

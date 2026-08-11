"""Select platform for operating mode and strategy."""

from __future__ import annotations

from homeassistant.components.select import SelectEntity, SelectEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import CONF_OPERATING_MODE, CONF_STRATEGY, OperatingMode, Strategy
from .entity import DeyeMRAutopilotEntity

SELECTS = (
    SelectEntityDescription(
        key=CONF_OPERATING_MODE,
        translation_key="autopilot_mode",
        icon="mdi:robot",
    ),
    SelectEntityDescription(
        key=CONF_STRATEGY,
        translation_key="strategy",
        icon="mdi:tune-variant",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up select entities."""
    async_add_entities(
        DeyeModeSelect(entry.runtime_data.coordinator, description)
        for description in SELECTS
    )


class DeyeModeSelect(DeyeMRAutopilotEntity, SelectEntity):
    """Safe runtime mode/strategy selection."""

    def __init__(self, coordinator, description: SelectEntityDescription) -> None:
        super().__init__(coordinator, description.key)
        self.entity_description = description
        if description.key == CONF_OPERATING_MODE:
            self._attr_options = [value.value for value in OperatingMode]
        else:
            self._attr_options = [value.value for value in Strategy]

    @property
    def current_option(self) -> str:
        """Return the current selected option."""
        runtime = self.coordinator.config_entry.runtime_data
        if self.entity_description.key == CONF_OPERATING_MODE:
            return runtime.operating_mode.value
        return runtime.strategy.value

    async def async_select_option(self, option: str) -> None:
        """Select an option and persist it in config-entry options."""
        entry = self.coordinator.config_entry
        options = dict(entry.options)
        if self.entity_description.key == CONF_OPERATING_MODE:
            options[CONF_OPERATING_MODE] = OperatingMode(option).value
        else:
            options[CONF_STRATEGY] = Strategy(option).value
        self.hass.config_entries.async_update_entry(entry, options=options)

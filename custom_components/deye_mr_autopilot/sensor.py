"""Sensor platform for Deye MR Autopilot."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .coordinator import CoordinatorData
from .entity import DeyeMRAutopilotEntity


@dataclass(frozen=True, kw_only=True)
class DeyeSensorDescription(SensorEntityDescription):
    """Describe a coordinator-backed status sensor."""

    value_fn: Callable[[CoordinatorData], Any]


SENSORS: tuple[DeyeSensorDescription, ...] = (
    DeyeSensorDescription(
        key="status",
        translation_key="status",
        value_fn=lambda data: data.status,
    ),
    DeyeSensorDescription(
        key="safety_status",
        translation_key="safety_status",
        icon="mdi:shield-check",
        value_fn=lambda data: data.safety_status,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up status sensors."""
    async_add_entities(
        DeyeStatusSensor(entry.runtime_data.coordinator, description)
        for description in SENSORS
    )


class DeyeStatusSensor(DeyeMRAutopilotEntity, SensorEntity):
    """A read-only status sensor."""

    entity_description: DeyeSensorDescription

    def __init__(self, coordinator, description: DeyeSensorDescription) -> None:
        super().__init__(coordinator, description.key)
        self.entity_description = description

    @property
    def native_value(self) -> Any:
        """Return the current status value."""
        return self.entity_description.value_fn(self.coordinator.data)

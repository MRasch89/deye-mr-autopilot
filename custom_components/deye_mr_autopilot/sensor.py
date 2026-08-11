"""Sensor platform for Deye MR Autopilot."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE,
    UnitOfEnergy,
    UnitOfPower,
    UnitOfTemperature,
    UnitOfTime,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .coordinator import CoordinatorData
from .entity import DeyeMRAutopilotEntity


@dataclass(frozen=True, kw_only=True)
class DeyeSensorDescription(SensorEntityDescription):
    """Describe a coordinator-backed status sensor."""

    value_fn: Callable[[CoordinatorData], Any]
    attributes_fn: Callable[[CoordinatorData], dict[str, Any]] | None = None


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
    DeyeSensorDescription(
        key="telemetry_quality",
        translation_key="telemetry_quality",
        icon="mdi:database-check",
        value_fn=lambda data: data.telemetry.quality,
        attributes_fn=lambda data: {
            "missing_entities": data.telemetry.missing_entities,
            "unavailable_entities": data.telemetry.unavailable_entities,
            "invalid_entities": data.telemetry.invalid_entities,
            "connected": data.telemetry.connected,
            "battery_alarm": data.telemetry.battery_alarm,
            "battery_fault": data.telemetry.battery_fault,
        },
    ),
    DeyeSensorDescription(
        key="source_age",
        translation_key="source_age",
        device_class=SensorDeviceClass.DURATION,
        native_unit_of_measurement=UnitOfTime.SECONDS,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        value_fn=lambda data: data.telemetry.source_age_seconds,
    ),
    DeyeSensorDescription(
        key="pv_power",
        translation_key="pv_power",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.telemetry.pv_power_w,
    ),
    DeyeSensorDescription(
        key="load_power",
        translation_key="load_power",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.telemetry.load_power_w,
    ),
    DeyeSensorDescription(
        key="grid_power",
        translation_key="grid_power",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.telemetry.grid_power_w,
        attributes_fn=lambda data: {"positive_value": "grid_import"},
    ),
    DeyeSensorDescription(
        key="battery_soc",
        translation_key="battery_soc",
        device_class=SensorDeviceClass.BATTERY,
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.telemetry.battery_soc,
    ),
    DeyeSensorDescription(
        key="battery_power",
        translation_key="battery_power",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.telemetry.battery_power_w,
        attributes_fn=lambda data: {
            "battery_state": data.telemetry.battery_state,
            "positive_value": "discharge",
        },
    ),
    DeyeSensorDescription(
        key="battery_temperature",
        translation_key="battery_temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.telemetry.battery_temperature_c,
    ),
    DeyeSensorDescription(
        key="inverter_temperature",
        translation_key="inverter_temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.telemetry.inverter_temperature_c,
    ),
    *(
        DeyeSensorDescription(
            key=key,
            translation_key=key,
            device_class=SensorDeviceClass.ENERGY,
            native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
            state_class=SensorStateClass.TOTAL_INCREASING,
            suggested_display_precision=1,
            value_fn=value_fn,
        )
        for key, value_fn in (
            ("today_production", lambda data: data.telemetry.today_production_kwh),
            (
                "today_load_consumption",
                lambda data: data.telemetry.today_load_consumption_kwh,
            ),
            ("today_grid_import", lambda data: data.telemetry.today_grid_import_kwh),
            ("today_grid_export", lambda data: data.telemetry.today_grid_export_kwh),
            (
                "today_battery_charge",
                lambda data: data.telemetry.today_battery_charge_kwh,
            ),
            (
                "today_battery_discharge",
                lambda data: data.telemetry.today_battery_discharge_kwh,
            ),
        )
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

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return diagnostic metadata for selected telemetry sensors."""
        if self.entity_description.attributes_fn is None:
            return None
        return self.entity_description.attributes_fn(self.coordinator.data)

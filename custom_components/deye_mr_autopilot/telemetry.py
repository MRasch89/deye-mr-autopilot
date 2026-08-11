"""Read-only Home Assistant entity telemetry collection."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from homeassistant.const import STATE_UNAVAILABLE, STATE_UNKNOWN
from homeassistant.core import HomeAssistant, State
from homeassistant.util import dt as dt_util


class TelemetryQuality(StrEnum):
    """Quality assigned to a collected telemetry snapshot."""

    VALID = "valid"
    PARTIAL = "partial"
    STALE = "stale"
    INVALID = "invalid"


@dataclass(frozen=True, slots=True)
class SourceSpec:
    """Describe one read-only source entity."""

    entity_id: str
    expected_unit: str | None = None
    essential: bool = False


SOURCE_SPECS: dict[str, SourceSpec] = {
    "pv_power_w": SourceSpec("sensor.deye_inverter_pv_power", "W", essential=True),
    "load_power_w": SourceSpec("sensor.deye_inverter_load_power", "W", essential=True),
    "grid_power_w": SourceSpec("sensor.deye_inverter_grid_power", "W", essential=True),
    "battery_soc": SourceSpec("sensor.deye_inverter_battery", "%", essential=True),
    "battery_power_w": SourceSpec(
        "sensor.deye_inverter_battery_power", "W", essential=True
    ),
    "battery_temperature_c": SourceSpec(
        "sensor.deye_inverter_battery_temperature", "°C"
    ),
    "inverter_temperature_c": SourceSpec("sensor.deye_inverter_temperature", "°C"),
    "today_production_kwh": SourceSpec("sensor.deye_inverter_today_production", "kWh"),
    "today_load_consumption_kwh": SourceSpec(
        "sensor.deye_inverter_today_load_consumption", "kWh"
    ),
    "today_grid_import_kwh": SourceSpec(
        "sensor.deye_inverter_today_energy_import", "kWh"
    ),
    "today_grid_export_kwh": SourceSpec(
        "sensor.deye_inverter_today_energy_export", "kWh"
    ),
    "today_battery_charge_kwh": SourceSpec(
        "sensor.deye_inverter_today_battery_charge", "kWh"
    ),
    "today_battery_discharge_kwh": SourceSpec(
        "sensor.deye_inverter_today_battery_discharge", "kWh"
    ),
}

CONNECTION_ENTITY = "binary_sensor.deye_inverter_connection"
BATTERY_ALARM_ENTITY = "binary_sensor.deye_inverter_battery_alarm"
BATTERY_FAULT_ENTITY = "binary_sensor.deye_inverter_battery_fault"
BATTERY_STATE_ENTITY = "sensor.deye_inverter_battery_state"


@dataclass(frozen=True, slots=True)
class TelemetrySnapshot:
    """Normalized, immutable read-only snapshot of the energy installation."""

    pv_power_w: float | None
    load_power_w: float | None
    grid_power_w: float | None
    battery_soc: float | None
    battery_power_w: float | None
    battery_temperature_c: float | None
    inverter_temperature_c: float | None
    today_production_kwh: float | None
    today_load_consumption_kwh: float | None
    today_grid_import_kwh: float | None
    today_grid_export_kwh: float | None
    today_battery_charge_kwh: float | None
    today_battery_discharge_kwh: float | None
    battery_state: str | None
    connected: bool | None
    battery_alarm: bool | None
    battery_fault: bool | None
    quality: TelemetryQuality
    source_age_seconds: float | None
    missing_entities: tuple[str, ...]
    unavailable_entities: tuple[str, ...]
    invalid_entities: tuple[str, ...]
    collected_at: datetime


def _binary_value(state: State | None) -> bool | None:
    if state is None or state.state in (STATE_UNKNOWN, STATE_UNAVAILABLE):
        return None
    if state.state == "on":
        return True
    if state.state == "off":
        return False
    return None


class HomeAssistantTelemetryCollector:
    """Collect states without calling services or writable entity methods."""

    def __init__(self, hass: HomeAssistant, stale_after_seconds: int) -> None:
        self._hass = hass
        self._stale_after_seconds = stale_after_seconds

    async def async_collect(self) -> TelemetrySnapshot:
        """Read a normalized snapshot from Home Assistant's state machine."""
        now = dt_util.utcnow()
        values: dict[str, float | None] = {}
        missing: list[str] = []
        unavailable: list[str] = []
        invalid: list[str] = []
        essential_ages: list[float] = []

        for key, spec in SOURCE_SPECS.items():
            state = self._hass.states.get(spec.entity_id)
            if state is None:
                missing.append(spec.entity_id)
                values[key] = None
                continue
            if state.state in (STATE_UNKNOWN, STATE_UNAVAILABLE):
                unavailable.append(spec.entity_id)
                values[key] = None
                continue
            if (
                spec.expected_unit is not None
                and state.attributes.get("unit_of_measurement") != spec.expected_unit
            ):
                invalid.append(spec.entity_id)
                values[key] = None
                continue
            try:
                values[key] = float(state.state)
            except TypeError, ValueError:
                invalid.append(spec.entity_id)
                values[key] = None
                continue
            if spec.essential:
                essential_ages.append(
                    max(0.0, (now - state.last_updated).total_seconds())
                )

        binary_states = {
            entity_id: self._hass.states.get(entity_id)
            for entity_id in (
                CONNECTION_ENTITY,
                BATTERY_ALARM_ENTITY,
                BATTERY_FAULT_ENTITY,
            )
        }
        for entity_id, state in binary_states.items():
            if state is None:
                missing.append(entity_id)
            elif state.state in (STATE_UNKNOWN, STATE_UNAVAILABLE):
                unavailable.append(entity_id)
            elif state.state not in ("on", "off"):
                invalid.append(entity_id)

        connected = _binary_value(binary_states[CONNECTION_ENTITY])
        battery_alarm = _binary_value(binary_states[BATTERY_ALARM_ENTITY])
        battery_fault = _binary_value(binary_states[BATTERY_FAULT_ENTITY])
        battery_state_obj = self._hass.states.get(BATTERY_STATE_ENTITY)
        if battery_state_obj is None:
            missing.append(BATTERY_STATE_ENTITY)
        elif battery_state_obj.state in (STATE_UNKNOWN, STATE_UNAVAILABLE):
            unavailable.append(BATTERY_STATE_ENTITY)
        battery_state = (
            battery_state_obj.state
            if battery_state_obj is not None
            and battery_state_obj.state not in (STATE_UNKNOWN, STATE_UNAVAILABLE)
            else None
        )

        essential_ids = {
            spec.entity_id for spec in SOURCE_SPECS.values() if spec.essential
        }
        essential_errors = essential_ids.intersection(
            (*missing, *unavailable, *invalid)
        )
        source_age = max(essential_ages) if essential_ages else None
        valid_essential_count = len(essential_ids) - len(essential_errors)

        if connected is False or valid_essential_count == 0:
            quality = TelemetryQuality.INVALID
        elif essential_errors:
            quality = TelemetryQuality.PARTIAL
        elif source_age is not None and source_age > self._stale_after_seconds:
            quality = TelemetryQuality.STALE
        else:
            quality = TelemetryQuality.VALID

        return TelemetrySnapshot(
            **values,
            battery_state=battery_state,
            connected=connected,
            battery_alarm=battery_alarm,
            battery_fault=battery_fault,
            quality=quality,
            source_age_seconds=source_age,
            missing_entities=tuple(sorted(missing)),
            unavailable_entities=tuple(sorted(unavailable)),
            invalid_entities=tuple(sorted(invalid)),
            collected_at=now,
        )

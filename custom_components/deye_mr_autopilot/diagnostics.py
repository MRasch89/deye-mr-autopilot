"""Diagnostics support for Deye MR Autopilot."""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import VERSION
from .telemetry import (
    BATTERY_ALARM_ENTITY,
    BATTERY_FAULT_ENTITY,
    BATTERY_STATE_ENTITY,
    CONNECTION_ENTITY,
    SOURCE_SPECS,
)

TO_REDACT = {
    "logger_ip",
    "logger_serial_number",
    "password",
    "token",
}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict[str, Any]:
    """Return safe config-entry diagnostics."""
    runtime = entry.runtime_data
    return {
        "integration_version": VERSION,
        "entry": async_redact_data(
            {"data": dict(entry.data), "options": dict(entry.options)}, TO_REDACT
        ),
        "operating_mode": runtime.operating_mode.value,
        "strategy": runtime.strategy.value,
        "control_armed": runtime.control_armed,
        "control_adapter": type(runtime.control).__name__,
        "telemetry_sources": {
            **{key: spec.entity_id for key, spec in SOURCE_SPECS.items()},
            "connection": CONNECTION_ENTITY,
            "battery_alarm": BATTERY_ALARM_ENTITY,
            "battery_fault": BATTERY_FAULT_ENTITY,
            "battery_state": BATTERY_STATE_ENTITY,
        },
        "coordinator": {
            "last_update_success": runtime.coordinator.last_update_success,
            "data": asdict(runtime.coordinator.data),
        },
    }

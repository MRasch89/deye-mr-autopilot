"""Tests for the read-only Home Assistant telemetry collector."""

from custom_components.deye_mr_autopilot.telemetry import (
    BATTERY_ALARM_ENTITY,
    BATTERY_FAULT_ENTITY,
    BATTERY_STATE_ENTITY,
    CONNECTION_ENTITY,
    SOURCE_SPECS,
    HomeAssistantTelemetryCollector,
    TelemetryQuality,
)


def _set_complete_source_data(hass) -> None:
    for index, spec in enumerate(SOURCE_SPECS.values(), start=1):
        hass.states.async_set(
            spec.entity_id,
            str(index),
            {"unit_of_measurement": spec.expected_unit},
        )
    hass.states.async_set(CONNECTION_ENTITY, "on")
    hass.states.async_set(BATTERY_ALARM_ENTITY, "off")
    hass.states.async_set(BATTERY_FAULT_ENTITY, "off")
    hass.states.async_set(BATTERY_STATE_ENTITY, "discharging")


async def test_collector_builds_valid_read_only_snapshot(hass) -> None:
    _set_complete_source_data(hass)

    snapshot = await HomeAssistantTelemetryCollector(
        hass, stale_after_seconds=120
    ).async_collect()

    assert snapshot.quality is TelemetryQuality.VALID
    assert snapshot.pv_power_w == 1
    assert snapshot.load_power_w == 2
    assert snapshot.battery_state == "discharging"
    assert snapshot.connected is True
    assert snapshot.missing_entities == ()
    assert snapshot.unavailable_entities == ()
    assert snapshot.invalid_entities == ()


async def test_collector_marks_incomplete_essential_data_partial(hass) -> None:
    pv_spec = SOURCE_SPECS["pv_power_w"]
    hass.states.async_set(
        pv_spec.entity_id,
        "1200",
        {"unit_of_measurement": pv_spec.expected_unit},
    )
    hass.states.async_set(CONNECTION_ENTITY, "on")

    snapshot = await HomeAssistantTelemetryCollector(
        hass, stale_after_seconds=120
    ).async_collect()

    assert snapshot.quality is TelemetryQuality.PARTIAL
    assert snapshot.pv_power_w == 1200
    assert "sensor.deye_inverter_load_power" in snapshot.missing_entities


async def test_collector_rejects_unit_mismatch_and_disconnection(hass) -> None:
    _set_complete_source_data(hass)
    pv_spec = SOURCE_SPECS["pv_power_w"]
    hass.states.async_set(
        pv_spec.entity_id,
        "1.2",
        {"unit_of_measurement": "kW"},
    )
    hass.states.async_set(CONNECTION_ENTITY, "off")

    snapshot = await HomeAssistantTelemetryCollector(
        hass, stale_after_seconds=120
    ).async_collect()

    assert snapshot.quality is TelemetryQuality.INVALID
    assert snapshot.pv_power_w is None
    assert pv_spec.entity_id in snapshot.invalid_entities
    assert snapshot.connected is False

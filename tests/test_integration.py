"""Integration setup and entity tests."""

from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er

from custom_components.deye_mr_autopilot.const import DOMAIN, MANUFACTURER, MODEL
from custom_components.deye_mr_autopilot.telemetry import (
    BATTERY_ALARM_ENTITY,
    BATTERY_FAULT_ENTITY,
    BATTERY_STATE_ENTITY,
    CONNECTION_ENTITY,
    SOURCE_SPECS,
)


def _set_source_states(hass) -> None:
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


async def test_setup_creates_device_and_entities(hass, mock_config_entry) -> None:
    _set_source_states(hass)
    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    device = dr.async_get(hass).async_get_device(
        identifiers={(DOMAIN, mock_config_entry.entry_id)}
    )
    assert device is not None
    assert device.manufacturer == MANUFACTURER
    assert device.model == MODEL

    states = hass.states.async_all()
    by_unique_suffix = {
        state.entity_id: state.state
        for state in states
        if state.entity_id.startswith(("sensor.", "select.", "switch."))
    }
    assert any(entity_id.endswith("_status") for entity_id in by_unique_suffix)
    assert any(entity_id.endswith("_safety_status") for entity_id in by_unique_suffix)
    assert any(entity_id.endswith("_autopilot_mode") for entity_id in by_unique_suffix)
    assert any(entity_id.endswith("_strategy") for entity_id in by_unique_suffix)
    assert any(entity_id.endswith("_control_armed") for entity_id in by_unique_suffix)

    entity_registry = er.async_get(hass)
    pv_power_id = entity_registry.async_get_entity_id(
        "sensor", DOMAIN, f"{mock_config_entry.entry_id}_pv_power"
    )
    quality_id = entity_registry.async_get_entity_id(
        "sensor", DOMAIN, f"{mock_config_entry.entry_id}_telemetry_quality"
    )
    assert pv_power_id is not None
    assert quality_id is not None
    assert float(hass.states.get(pv_power_id).state) == 1
    assert hass.states.get(quality_id).state == "valid"

    runtime = mock_config_entry.runtime_data
    assert runtime.control_armed is False
    assert runtime.control.supports_physical_control is False


async def test_unload_entry(hass, mock_config_entry) -> None:
    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()
    assert await hass.config_entries.async_unload(mock_config_entry.entry_id)


async def test_control_arming_is_hard_blocked(hass, mock_config_entry) -> None:
    """The exposed Phase 1 switch must never arm hardware."""
    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    entity_id = er.async_get(hass).async_get_entity_id(
        "switch", DOMAIN, f"{mock_config_entry.entry_id}_control_armed"
    )
    assert entity_id is not None

    events = []
    hass.bus.async_listen(f"{DOMAIN}_control_arm_blocked", events.append)
    await hass.services.async_call(
        "switch", "turn_on", {"entity_id": entity_id}, blocking=True
    )

    assert hass.states.get(entity_id).state == "off"
    assert len(events) == 1
    assert events[0].data["reason"] == "physical_control_not_implemented"

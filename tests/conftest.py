"""Shared test fixtures."""

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.deye_mr_autopilot.const import (
    CONF_BATTERY_CAPACITY_KWH,
    CONF_BATTERY_CHEMISTRY,
    CONF_BATTERY_USABLE_CAPACITY_KWH,
    CONF_EMERGENCY_SOC,
    CONF_INSTALLATION_NAME,
    CONF_INVERTER_MANUFACTURER,
    CONF_INVERTER_MODEL,
    CONF_INVERTER_POWER_W,
    CONF_MAX_CHARGE_POWER_W,
    CONF_MAX_DISCHARGE_POWER_W,
    CONF_MAXIMUM_SOC,
    CONF_MINIMUM_SOC,
    CONF_PV_PEAK_POWER_W,
    CONF_RECOVERY_SOC,
    DOMAIN,
)


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Enable loading custom integrations in every test."""


@pytest.fixture
def installation_data() -> dict:
    """Return a complete valid installation data mapping."""
    return {
        CONF_INSTALLATION_NAME: "Home Energy System",
        CONF_INVERTER_MANUFACTURER: "Deye",
        CONF_INVERTER_MODEL: "SUN-6K-SG05LP3-EU",
        CONF_INVERTER_POWER_W: 6000,
        CONF_PV_PEAK_POWER_W: 7200,
        CONF_BATTERY_CAPACITY_KWH: 15.0,
        CONF_BATTERY_USABLE_CAPACITY_KWH: 13.5,
        CONF_BATTERY_CHEMISTRY: "LFP",
        CONF_EMERGENCY_SOC: 20,
        CONF_MINIMUM_SOC: 30,
        CONF_RECOVERY_SOC: 55,
        CONF_MAXIMUM_SOC: 90,
        CONF_MAX_CHARGE_POWER_W: 6000,
        CONF_MAX_DISCHARGE_POWER_W: 6000,
    }


@pytest.fixture
def mock_config_entry(hass, installation_data) -> MockConfigEntry:
    """Create and register a mock config entry."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Home Energy System",
        data=installation_data,
        unique_id="home_energy_system",
    )
    entry.add_to_hass(hass)
    return entry

"""Tests for installation configuration."""

import pytest

from custom_components.deye_mr_autopilot.const import (
    CONF_BATTERY_USABLE_CAPACITY_KWH,
    CONF_EMERGENCY_SOC,
    CONF_MINIMUM_SOC,
)
from custom_components.deye_mr_autopilot.models import InstallationConfig


def test_installation_config_accepts_valid_values(installation_data) -> None:
    config = InstallationConfig.from_mapping(installation_data)
    assert config.battery_nominal_capacity_kwh == 15.0
    assert config.emergency_soc == 20
    assert config.minimum_soc == 30


def test_installation_config_rejects_bad_soc_order(installation_data) -> None:
    installation_data[CONF_EMERGENCY_SOC] = 40
    installation_data[CONF_MINIMUM_SOC] = 30
    with pytest.raises(ValueError, match="SOC limits"):
        InstallationConfig.from_mapping(installation_data)


def test_installation_config_rejects_usable_capacity_over_nominal(
    installation_data,
) -> None:
    installation_data[CONF_BATTERY_USABLE_CAPACITY_KWH] = 16
    with pytest.raises(ValueError, match="usable battery"):
        InstallationConfig.from_mapping(installation_data)

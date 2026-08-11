"""Constants for Deye MR Autopilot."""

from datetime import timedelta
from enum import StrEnum

from homeassistant.const import Platform

DOMAIN = "deye_mr_autopilot"
NAME = "Deye MR Autopilot"
MANUFACTURER = "MR"
MODEL = "Energy Management Autopilot"
VERSION = "0.1.0-alpha.1"

PLATFORMS: tuple[Platform, ...] = (
    Platform.SENSOR,
    Platform.SELECT,
    Platform.SWITCH,
)

CONF_INSTALLATION_NAME = "installation_name"
CONF_INVERTER_MANUFACTURER = "inverter_manufacturer"
CONF_INVERTER_MODEL = "inverter_model"
CONF_INVERTER_POWER_W = "inverter_nominal_power_w"
CONF_PV_PEAK_POWER_W = "pv_peak_power_w"
CONF_BATTERY_CAPACITY_KWH = "battery_nominal_capacity_kwh"
CONF_BATTERY_USABLE_CAPACITY_KWH = "battery_usable_capacity_kwh"
CONF_BATTERY_CHEMISTRY = "battery_chemistry"
CONF_MINIMUM_SOC = "minimum_soc"
CONF_EMERGENCY_SOC = "emergency_soc"
CONF_MAXIMUM_SOC = "maximum_soc"
CONF_RECOVERY_SOC = "recovery_soc"
CONF_MAX_CHARGE_POWER_W = "maximum_charge_power_w"
CONF_MAX_DISCHARGE_POWER_W = "maximum_discharge_power_w"
CONF_DATA_SOURCE_MODE = "data_source_mode"
CONF_OPERATING_MODE = "operating_mode"
CONF_STRATEGY = "strategy"
CONF_UPDATE_INTERVAL = "update_interval_seconds"

DEFAULT_INVERTER_MANUFACTURER = "Deye"
DEFAULT_INVERTER_MODEL = "SUN-6K-SG05LP3-EU"
DEFAULT_INVERTER_POWER_W = 6000
DEFAULT_PV_PEAK_POWER_W = 6000
DEFAULT_BATTERY_CAPACITY_KWH = 15.0
DEFAULT_MINIMUM_SOC = 30
DEFAULT_EMERGENCY_SOC = 20
DEFAULT_MAXIMUM_SOC = 90
DEFAULT_RECOVERY_SOC = 55
DEFAULT_MAX_CHARGE_POWER_W = 6000
DEFAULT_MAX_DISCHARGE_POWER_W = 6000
DEFAULT_UPDATE_INTERVAL = 60
MIN_UPDATE_INTERVAL = 30
MAX_UPDATE_INTERVAL = 3600

COORDINATOR_UPDATE_INTERVAL = timedelta(seconds=DEFAULT_UPDATE_INTERVAL)


class OperatingMode(StrEnum):
    """Supported operating modes."""

    OFF = "off"
    MONITOR = "monitor"
    RECOMMEND = "recommend"
    SHADOW = "shadow"
    AUTOPILOT = "autopilot"


class Strategy(StrEnum):
    """Supported energy strategies."""

    SAFE = "safe"
    BALANCED = "balanced"
    SELF_CONSUMPTION = "self_consumption"
    PROFIT = "profit"
    BACKUP = "backup"
    CUSTOM = "custom"


class DataSourceMode(StrEnum):
    """Supported data-source topologies."""

    HOME_ASSISTANT = "home_assistant"
    DIRECT_SOLARMAN = "direct_solarman"
    HYBRID = "hybrid"


DEFAULT_OPERATING_MODE = OperatingMode.MONITOR
DEFAULT_STRATEGY = Strategy.BALANCED
DEFAULT_DATA_SOURCE_MODE = DataSourceMode.HOME_ASSISTANT

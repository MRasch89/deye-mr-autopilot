"""Shared typed models for Deye MR Autopilot."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from .const import (
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
    DEFAULT_OPERATING_MODE,
    DEFAULT_STRATEGY,
    OperatingMode,
    Strategy,
)

if TYPE_CHECKING:
    from .agent.base import AgentGraph
    from .control.base import ControlAdapter
    from .coordinator import DeyeMRAutopilotCoordinator
    from .optimizer.base import OptimizationProvider
    from .safety.engine import SafetyEngine


@dataclass(frozen=True, slots=True)
class InstallationConfig:
    """Validated installation configuration."""

    name: str
    inverter_manufacturer: str
    inverter_model: str
    inverter_nominal_power_w: int
    pv_peak_power_w: int
    battery_nominal_capacity_kwh: float
    battery_usable_capacity_kwh: float | None
    battery_chemistry: str | None
    minimum_soc: int
    emergency_soc: int
    maximum_soc: int
    recovery_soc: int
    maximum_charge_power_w: int
    maximum_discharge_power_w: int

    @classmethod
    def from_mapping(cls, data: dict[str, Any]) -> InstallationConfig:
        """Create and validate installation configuration from entry data."""
        config = cls(
            name=str(data[CONF_INSTALLATION_NAME]).strip(),
            inverter_manufacturer=str(data[CONF_INVERTER_MANUFACTURER]).strip(),
            inverter_model=str(data[CONF_INVERTER_MODEL]).strip(),
            inverter_nominal_power_w=int(data[CONF_INVERTER_POWER_W]),
            pv_peak_power_w=int(data[CONF_PV_PEAK_POWER_W]),
            battery_nominal_capacity_kwh=float(data[CONF_BATTERY_CAPACITY_KWH]),
            battery_usable_capacity_kwh=(
                float(data[CONF_BATTERY_USABLE_CAPACITY_KWH])
                if data.get(CONF_BATTERY_USABLE_CAPACITY_KWH) not in (None, "")
                else None
            ),
            battery_chemistry=(
                str(data[CONF_BATTERY_CHEMISTRY]).strip()
                if data.get(CONF_BATTERY_CHEMISTRY)
                else None
            ),
            minimum_soc=int(data[CONF_MINIMUM_SOC]),
            emergency_soc=int(data[CONF_EMERGENCY_SOC]),
            maximum_soc=int(data[CONF_MAXIMUM_SOC]),
            recovery_soc=int(data[CONF_RECOVERY_SOC]),
            maximum_charge_power_w=int(data[CONF_MAX_CHARGE_POWER_W]),
            maximum_discharge_power_w=int(data[CONF_MAX_DISCHARGE_POWER_W]),
        )
        config.validate()
        return config

    def validate(self) -> None:
        """Validate cross-field safety constraints."""
        if not self.name:
            raise ValueError("installation name is required")
        if self.inverter_nominal_power_w <= 0 or self.pv_peak_power_w <= 0:
            raise ValueError("power values must be positive")
        if self.battery_nominal_capacity_kwh <= 0:
            raise ValueError("battery capacity must be positive")
        if (
            self.battery_usable_capacity_kwh is not None
            and self.battery_usable_capacity_kwh > self.battery_nominal_capacity_kwh
        ):
            raise ValueError("usable battery capacity cannot exceed nominal capacity")
        if not (
            0
            <= self.emergency_soc
            <= self.minimum_soc
            < self.recovery_soc
            <= self.maximum_soc
            <= 100
        ):
            raise ValueError(
                "SOC limits must satisfy emergency <= minimum < recovery <= maximum"
            )
        if self.maximum_charge_power_w <= 0 or self.maximum_discharge_power_w <= 0:
            raise ValueError("battery power limits must be positive")


@dataclass(slots=True)
class DeyeRuntimeData:
    """Objects owned by a loaded config entry."""

    installation: InstallationConfig
    coordinator: DeyeMRAutopilotCoordinator
    control: ControlAdapter
    optimizer: OptimizationProvider
    agent_graph: AgentGraph
    safety: SafetyEngine
    operating_mode: OperatingMode = DEFAULT_OPERATING_MODE
    strategy: Strategy = DEFAULT_STRATEGY
    control_armed: bool = False

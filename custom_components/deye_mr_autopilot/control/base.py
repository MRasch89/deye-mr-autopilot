"""High-level control adapter contract."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Any, Protocol

from homeassistant.util import dt as dt_util


class ControlAction(StrEnum):
    """Allowlisted high-level control intents."""

    SET_WORK_MODE = "SET_WORK_MODE"
    SET_EXPORT_LIMIT = "SET_EXPORT_LIMIT"
    SET_TARGET_SOC = "SET_TARGET_SOC"
    SET_GRID_CHARGE_ENABLED = "SET_GRID_CHARGE_ENABLED"
    SET_GRID_CHARGE_POWER = "SET_GRID_CHARGE_POWER"
    SET_BATTERY_DISCHARGE_LIMIT = "SET_BATTERY_DISCHARGE_LIMIT"


@dataclass(frozen=True, slots=True)
class ControlCommand:
    """Validated high-level command; never a raw register write."""

    action: ControlAction
    parameters: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=dt_util.utcnow)


@dataclass(frozen=True, slots=True)
class ControlResult:
    """Control execution and verification outcome."""

    success: bool
    verified: bool
    message: str


class ControlAdapter(Protocol):
    """Only legal route from a safe decision toward future hardware control."""

    @property
    def supports_physical_control(self) -> bool:
        """Return whether this adapter can reach physical hardware."""
        ...

    async def async_execute(self, command: ControlCommand) -> ControlResult:
        """Execute one allowlisted high-level command."""
        ...

    async def async_verify_state(self, command: ControlCommand) -> bool:
        """Read back and verify expected state."""
        ...

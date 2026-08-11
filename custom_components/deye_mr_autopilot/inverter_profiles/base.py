"""Inverter profile foundation with no raw register API."""

from dataclasses import dataclass

from ..control.base import ControlAction


@dataclass(frozen=True, slots=True)
class InverterProfile:
    """Model-specific allowlist of verified high-level actions."""

    manufacturer: str
    model: str
    supported_actions: frozenset[ControlAction]
    control_verified: bool = False

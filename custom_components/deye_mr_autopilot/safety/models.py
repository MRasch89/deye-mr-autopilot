"""Safety domain models."""

from dataclasses import dataclass

from ..control.base import ControlCommand


@dataclass(frozen=True, slots=True)
class SafetyResult:
    """Final safety approval or rejection."""

    approved: bool
    command: ControlCommand | None
    reason: str

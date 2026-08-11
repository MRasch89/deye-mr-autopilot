"""Final-authority safety engine."""

from typing import Any

from ..control.base import ControlCommand
from .models import SafetyResult


class SafetyEngine:
    """Block all physical control until later safety phases are implemented."""

    async def async_validate(
        self, command: ControlCommand | None, snapshot: Any | None
    ) -> SafetyResult:
        """Return a safe rejection in Phase 1."""
        return SafetyResult(
            approved=False,
            command=None,
            reason="Physical control is disabled in Phase 1",
        )

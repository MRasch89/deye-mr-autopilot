"""Future direct Solarman adapter boundary."""

from .base import ControlCommand, ControlResult


class SolarmanControlAdapter:
    """Disabled until a model-specific writable-register profile is verified."""

    @property
    def supports_physical_control(self) -> bool:
        return False

    async def async_execute(self, command: ControlCommand) -> ControlResult:
        return ControlResult(False, False, "Direct Solarman control is disabled")

    async def async_verify_state(self, command: ControlCommand) -> bool:
        return False

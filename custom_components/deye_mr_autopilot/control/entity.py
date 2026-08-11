"""Future Home Assistant entity control adapter boundary."""

from .base import ControlCommand, ControlResult


class EntityControlAdapter:
    """Disabled Phase 1 placeholder for explicitly mapped writable entities."""

    @property
    def supports_physical_control(self) -> bool:
        return False

    async def async_execute(self, command: ControlCommand) -> ControlResult:
        return ControlResult(False, False, "Entity control is not implemented")

    async def async_verify_state(self, command: ControlCommand) -> bool:
        return False

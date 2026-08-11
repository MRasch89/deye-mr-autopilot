"""Non-physical mock control adapter."""

from .base import ControlAdapter, ControlCommand, ControlResult


class MockControlAdapter(ControlAdapter):
    """Record commands in memory without any hardware I/O."""

    def __init__(self) -> None:
        self.commands: list[ControlCommand] = []

    @property
    def supports_physical_control(self) -> bool:
        return False

    async def async_execute(self, command: ControlCommand) -> ControlResult:
        self.commands.append(command)
        verified = await self.async_verify_state(command)
        return ControlResult(
            success=True,
            verified=verified,
            message="Mock command recorded; no hardware was contacted",
        )

    async def async_verify_state(self, command: ControlCommand) -> bool:
        return command in self.commands

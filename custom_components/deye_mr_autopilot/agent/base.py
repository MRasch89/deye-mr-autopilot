"""Agent graph contract."""

from typing import Protocol

from .state import AgentState


class AgentGraph(Protocol):
    """Execute a deterministic decision graph over typed state."""

    async def async_run(self, state: AgentState) -> AgentState:
        """Run the graph and return the resulting state."""
        ...

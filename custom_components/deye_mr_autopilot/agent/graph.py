"""Native and optional LangGraph agent graph implementations."""

from __future__ import annotations

from importlib.util import find_spec
from typing import Any, TypedDict

from .state import AgentState


class NativeAgentGraph:
    """Small deterministic fallback graph that is always available."""

    async def async_run(self, state: AgentState) -> AgentState:
        """Validate Phase 1 state and force a safe no-action result."""
        if state.installation_snapshot is None:
            state.data_quality = "INVALID"
            state.proposed_action = "NO_ACTION"
            state.safety_status = "SAFE"
            state.reason = "Installation snapshot unavailable in Phase 1"
        return state


class _LangGraphState(TypedDict):
    agent_state: AgentState


class LangGraphAgentGraph:
    """Optional in-process LangGraph implementation behind AgentGraph."""

    def __init__(self) -> None:
        if not self.is_available():
            raise RuntimeError("LangGraph is not installed")
        from langgraph.graph import END, START, StateGraph

        async def safe_no_action(graph_state: _LangGraphState) -> _LangGraphState:
            state = await NativeAgentGraph().async_run(graph_state["agent_state"])
            return {"agent_state": state}

        builder: Any = StateGraph(_LangGraphState)
        builder.add_node("safe_no_action", safe_no_action)
        builder.add_edge(START, "safe_no_action")
        builder.add_edge("safe_no_action", END)
        self._graph = builder.compile()

    @staticmethod
    def is_available() -> bool:
        """Return whether the optional library can be imported."""
        return find_spec("langgraph") is not None

    async def async_run(self, state: AgentState) -> AgentState:
        """Run the optional graph entirely in-process."""
        result = await self._graph.ainvoke({"agent_state": state})
        return result["agent_state"]

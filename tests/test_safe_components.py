"""Tests for safe Phase 1 components."""

from custom_components.deye_mr_autopilot.agent.graph import NativeAgentGraph
from custom_components.deye_mr_autopilot.agent.state import AgentState
from custom_components.deye_mr_autopilot.control.base import (
    ControlAction,
    ControlCommand,
)
from custom_components.deye_mr_autopilot.control.mock import MockControlAdapter
from custom_components.deye_mr_autopilot.optimizer.fallback import SafeFallbackOptimizer
from custom_components.deye_mr_autopilot.optimizer.models import RecommendedAction
from custom_components.deye_mr_autopilot.safety.engine import SafetyEngine


async def test_mock_control_records_without_physical_control() -> None:
    adapter = MockControlAdapter()
    command = ControlCommand(ControlAction.SET_TARGET_SOC, {"target_soc": 80})
    result = await adapter.async_execute(command)
    assert result.success is True
    assert result.verified is True
    assert adapter.supports_physical_control is False
    assert adapter.commands == [command]


async def test_safety_engine_blocks_every_command() -> None:
    command = ControlCommand(ControlAction.SET_EXPORT_LIMIT, {"limit_w": 1000})
    result = await SafetyEngine().async_validate(command, snapshot=object())
    assert result.approved is False
    assert result.command is None


async def test_safe_fallback_optimizer_emits_no_action() -> None:
    plan = await SafeFallbackOptimizer().async_create_plan(None, strategy="BALANCED")
    assert plan.fallback is True
    assert len(plan.points) == 1
    assert plan.points[0].recommended_action is RecommendedAction.NO_ACTION


async def test_native_graph_invalid_snapshot_is_no_action() -> None:
    state = await NativeAgentGraph().async_run(AgentState())
    assert state.data_quality == "INVALID"
    assert state.proposed_action == "NO_ACTION"
    assert state.safety_status == "SAFE"

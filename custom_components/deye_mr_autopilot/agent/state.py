"""Strongly typed agent state foundation."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from homeassistant.util import dt as dt_util


@dataclass(slots=True)
class AgentState:
    """State passed through native or optional LangGraph execution."""

    timestamp: datetime = field(default_factory=dt_util.utcnow)
    installation_snapshot: Any | None = None
    operating_mode: str = "MONITOR"
    strategy: str = "BALANCED"
    data_quality: str = "INVALID"
    proposed_action: str = "NO_ACTION"
    safety_status: str = "SAFE"
    reason: str = "Phase 1 has no installation data layer"

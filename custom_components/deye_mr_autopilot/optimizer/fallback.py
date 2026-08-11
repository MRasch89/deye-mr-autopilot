"""Deterministic safe fallback optimizer."""

from datetime import timedelta
from typing import Any

from homeassistant.util import dt as dt_util

from .models import OptimizationPlan, OptimizationPoint, RecommendedAction


class SafeFallbackOptimizer:
    """Always return a conservative no-action plan in Phase 1."""

    async def async_create_plan(
        self, snapshot: Any, *, strategy: str
    ) -> OptimizationPlan:
        """Create a one-point plan that cannot command hardware."""
        now = dt_util.utcnow()
        return OptimizationPlan(
            created_at=now,
            valid_until=now + timedelta(minutes=30),
            interval_minutes=30,
            strategy=strategy,
            points=(
                OptimizationPoint(
                    timestamp=now,
                    recommended_action=RecommendedAction.NO_ACTION,
                    reason="Phase 1 safe fallback: physical control is unavailable",
                ),
            ),
            fallback=True,
        )

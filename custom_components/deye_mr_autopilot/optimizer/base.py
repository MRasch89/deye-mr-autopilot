"""Optimization provider contract."""

from typing import Any, Protocol

from .models import OptimizationPlan


class OptimizationProvider(Protocol):
    """Produce a bounded, high-level energy plan."""

    async def async_create_plan(
        self, snapshot: Any, *, strategy: str
    ) -> OptimizationPlan:
        """Create a plan without performing physical control."""
        ...

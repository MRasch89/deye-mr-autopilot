"""Learning engine contract and safe null implementation."""

from typing import Any, Protocol


class LearningEngine(Protocol):
    """Update bounded local statistical models from observed outcomes."""

    async def async_observe(self, observation: Any) -> None:
        """Observe an outcome without external telemetry."""
        ...


class NullLearningEngine:
    """No-op Phase 1 learning implementation."""

    async def async_observe(self, observation: Any) -> None:
        return None

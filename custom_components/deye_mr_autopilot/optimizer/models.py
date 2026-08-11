"""Optimization domain models."""

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


class RecommendedAction(StrEnum):
    """Safe high-level optimizer actions."""

    NO_ACTION = "NO_ACTION"


@dataclass(frozen=True, slots=True)
class OptimizationPoint:
    """One point in an optimization plan."""

    timestamp: datetime
    recommended_action: RecommendedAction
    reason: str


@dataclass(frozen=True, slots=True)
class OptimizationPlan:
    """Bounded optimization plan."""

    created_at: datetime
    valid_until: datetime
    interval_minutes: int
    strategy: str
    points: tuple[OptimizationPoint, ...]
    fallback: bool = False

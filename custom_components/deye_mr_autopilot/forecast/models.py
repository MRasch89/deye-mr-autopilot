"""Forecast domain models."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class ForecastSnapshot:
    """Normalized forecast summary used by future phases."""

    generated_at: datetime
    source: str
    today_kwh: float | None = None
    remaining_today_kwh: float | None = None
    tomorrow_kwh: float | None = None
    day_2_kwh: float | None = None
    confidence: float = 0.0

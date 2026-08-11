"""Weather domain models."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class WeatherSnapshot:
    """Supplementary weather data from Home Assistant."""

    generated_at: datetime
    source_entity_id: str
    condition: str | None = None
    temperature_c: float | None = None
    cloud_coverage_percent: float | None = None
    confidence: float = 0.0

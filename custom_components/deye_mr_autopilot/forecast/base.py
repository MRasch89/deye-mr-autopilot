"""Solar forecast provider contract."""

from typing import Protocol

from .models import ForecastSnapshot


class ForecastProvider(Protocol):
    """Provide a normalized solar forecast without owning a cloud service."""

    async def async_get_forecast(self) -> ForecastSnapshot | None:
        """Return the latest forecast or None when unavailable."""
        ...

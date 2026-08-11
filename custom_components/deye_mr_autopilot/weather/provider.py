"""Weather provider contract."""

from typing import Protocol

from .models import WeatherSnapshot


class WeatherProvider(Protocol):
    """Provide weather already available inside Home Assistant."""

    async def async_get_weather(self) -> WeatherSnapshot | None:
        """Return the latest weather snapshot or None."""
        ...

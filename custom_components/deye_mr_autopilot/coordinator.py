"""Coordinator for integration state and read-only telemetry."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.util import dt as dt_util

from .const import (
    CONF_UPDATE_INTERVAL,
    DEFAULT_UPDATE_INTERVAL,
    DOMAIN,
    OperatingMode,
    Strategy,
)
from .telemetry import (
    HomeAssistantTelemetryCollector,
    TelemetryQuality,
    TelemetrySnapshot,
)

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class CoordinatorData:
    """Comparable integration state exposed to entities."""

    status: str
    safety_status: str
    optimization_status: str
    agent_status: str
    control_connection_status: str
    telemetry: TelemetrySnapshot
    last_update: datetime


class DeyeMRAutopilotCoordinator(DataUpdateCoordinator[CoordinatorData]):
    """Coordinate entity-state reads without any physical device writes."""

    config_entry: ConfigEntry

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        interval = int(entry.options.get(CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL))
        self._telemetry = HomeAssistantTelemetryCollector(
            hass,
            stale_after_seconds=max(120, interval * 3),
        )
        super().__init__(
            hass,
            _LOGGER,
            config_entry=entry,
            name=DOMAIN,
            update_interval=timedelta(seconds=interval),
            always_update=False,
        )

    async def _async_update_data(self) -> CoordinatorData:
        runtime = self.config_entry.runtime_data
        mode = OperatingMode(runtime.operating_mode)
        strategy = Strategy(runtime.strategy)
        telemetry = await self._telemetry.async_collect()

        if mode is OperatingMode.AUTOPILOT:
            safety_status = "control_unavailable"
        elif telemetry.battery_fault:
            safety_status = "battery_fault"
        elif telemetry.battery_alarm:
            safety_status = "battery_alarm"
        elif telemetry.connected is False:
            safety_status = "source_disconnected"
        elif telemetry.quality is TelemetryQuality.INVALID:
            safety_status = "telemetry_unavailable"
        elif telemetry.quality is TelemetryQuality.PARTIAL:
            safety_status = "telemetry_partial"
        elif telemetry.quality is TelemetryQuality.STALE:
            safety_status = "data_stale"
        else:
            safety_status = "safe"

        return CoordinatorData(
            status=("off" if mode is OperatingMode.OFF else "monitoring"),
            safety_status=safety_status,
            optimization_status=f"read_only_{strategy.value.lower()}",
            agent_status="native_fallback_ready",
            control_connection_status="mock_only",
            telemetry=telemetry,
            last_update=dt_util.utcnow(),
        )

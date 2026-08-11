"""Coordinator for the Phase 1 integration state."""

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

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class CoordinatorData:
    """Small, comparable Phase 1 state exposed to entities."""

    status: str
    safety_status: str
    optimization_status: str
    agent_status: str
    control_connection_status: str
    last_update: datetime


class DeyeMRAutopilotCoordinator(DataUpdateCoordinator[CoordinatorData]):
    """Coordinate lightweight integration status without device I/O."""

    config_entry: ConfigEntry

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        interval = int(entry.options.get(CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL))
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
        return CoordinatorData(
            status=("off" if mode is OperatingMode.OFF else "monitoring"),
            safety_status=(
                "control_unavailable" if mode is OperatingMode.AUTOPILOT else "safe"
            ),
            optimization_status=f"phase_1_{strategy.value.lower()}",
            agent_status="native_fallback_ready",
            control_connection_status="mock_only",
            last_update=dt_util.utcnow(),
        )

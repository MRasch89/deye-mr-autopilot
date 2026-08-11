"""Deye MR Autopilot Home Assistant integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr

from .agent.graph import NativeAgentGraph
from .const import (
    CONF_OPERATING_MODE,
    CONF_STRATEGY,
    DEFAULT_OPERATING_MODE,
    DEFAULT_STRATEGY,
    DOMAIN,
    MANUFACTURER,
    MODEL,
    PLATFORMS,
    VERSION,
    OperatingMode,
    Strategy,
)
from .control.mock import MockControlAdapter
from .coordinator import DeyeMRAutopilotCoordinator
from .models import DeyeRuntimeData, InstallationConfig
from .optimizer.fallback import SafeFallbackOptimizer
from .safety.engine import SafetyEngine


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Deye MR Autopilot from a config entry."""
    installation = InstallationConfig.from_mapping(dict(entry.data))
    coordinator = DeyeMRAutopilotCoordinator(hass, entry)
    entry.runtime_data = DeyeRuntimeData(
        installation=installation,
        coordinator=coordinator,
        control=MockControlAdapter(),
        optimizer=SafeFallbackOptimizer(),
        agent_graph=NativeAgentGraph(),
        safety=SafetyEngine(),
        operating_mode=OperatingMode(
            entry.options.get(CONF_OPERATING_MODE, DEFAULT_OPERATING_MODE)
        ),
        strategy=Strategy(entry.options.get(CONF_STRATEGY, DEFAULT_STRATEGY)),
    )

    device_registry = dr.async_get(hass)
    device_registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, entry.entry_id)},
        name="Deye MR Autopilot",
        manufacturer=MANUFACTURER,
        model=MODEL,
        sw_version=VERSION,
    )

    await coordinator.async_config_entry_first_refresh()
    entry.async_on_unload(entry.add_update_listener(_async_reload_entry))
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def _async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload when entry options change."""
    await hass.config_entries.async_reload(entry.entry_id)

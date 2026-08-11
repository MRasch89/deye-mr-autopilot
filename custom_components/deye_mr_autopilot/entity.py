"""Base entity for Deye MR Autopilot."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MANUFACTURER, MODEL, VERSION
from .coordinator import DeyeMRAutopilotCoordinator


class DeyeMRAutopilotEntity(CoordinatorEntity[DeyeMRAutopilotCoordinator]):
    """Base coordinator entity tied to the logical Autopilot device."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: DeyeMRAutopilotCoordinator, key: str) -> None:
        super().__init__(coordinator)
        entry = coordinator.config_entry
        self._attr_unique_id = f"{entry.entry_id}_{key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="Deye MR Autopilot",
            manufacturer=MANUFACTURER,
            model=MODEL,
            sw_version=VERSION,
        )

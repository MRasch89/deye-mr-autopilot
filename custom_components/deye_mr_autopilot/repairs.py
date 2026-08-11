"""Repair issue helpers for Deye MR Autopilot."""

from homeassistant.core import HomeAssistant
from homeassistant.helpers import issue_registry as ir

from .const import DOMAIN


def async_create_control_blocked_issue(hass: HomeAssistant, entry_id: str) -> None:
    """Create a repair issue when a future control path is disarmed."""
    ir.async_create_issue(
        hass,
        DOMAIN,
        f"control_blocked_{entry_id}",
        is_fixable=False,
        severity=ir.IssueSeverity.ERROR,
        translation_key="control_blocked",
        translation_placeholders={"entry_id": entry_id},
    )

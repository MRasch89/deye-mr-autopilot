"""Diagnostics tests."""

from custom_components.deye_mr_autopilot.diagnostics import (
    async_get_config_entry_diagnostics,
)


async def test_diagnostics_are_safe(hass, mock_config_entry) -> None:
    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()
    diagnostics = await async_get_config_entry_diagnostics(hass, mock_config_entry)
    assert diagnostics["control_armed"] is False
    assert diagnostics["control_adapter"] == "MockControlAdapter"
    assert "password" not in str(diagnostics)

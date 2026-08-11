"""Tests for config, options, and reconfigure flows."""

from homeassistant import config_entries, data_entry_flow

from custom_components.deye_mr_autopilot.const import (
    CONF_BATTERY_USABLE_CAPACITY_KWH,
    CONF_DATA_SOURCE_MODE,
    CONF_EMERGENCY_SOC,
    CONF_MAXIMUM_SOC,
    CONF_MINIMUM_SOC,
    CONF_OPERATING_MODE,
    CONF_RECOVERY_SOC,
    CONF_STRATEGY,
    CONF_UPDATE_INTERVAL,
    DOMAIN,
    DataSourceMode,
    OperatingMode,
    Strategy,
)


def _flow_input(installation_data: dict) -> dict:
    user_input = dict(installation_data)
    user_input["soc_limits"] = {
        key: user_input.pop(key)
        for key in (
            CONF_EMERGENCY_SOC,
            CONF_MINIMUM_SOC,
            CONF_RECOVERY_SOC,
            CONF_MAXIMUM_SOC,
        )
    }
    return user_input


async def test_user_flow_creates_entry(hass, installation_data) -> None:
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] is data_entry_flow.FlowResultType.FORM
    assert result["step_id"] == "user"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], _flow_input(installation_data)
    )
    assert result["type"] is data_entry_flow.FlowResultType.CREATE_ENTRY
    assert result["title"] == "Home Energy System"
    assert result["data"][CONF_MINIMUM_SOC] == 30
    assert "soc_limits" not in result["data"]


async def test_user_flow_allows_empty_usable_battery_capacity(
    hass, installation_data
) -> None:
    installation_data.pop(CONF_BATTERY_USABLE_CAPACITY_KWH)
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], _flow_input(installation_data)
    )

    assert result["type"] is data_entry_flow.FlowResultType.CREATE_ENTRY
    assert CONF_BATTERY_USABLE_CAPACITY_KWH not in result["data"]


async def test_user_flow_rejects_inconsistent_limits(hass, installation_data) -> None:
    flow = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    user_input = _flow_input(installation_data)
    user_input["soc_limits"][CONF_EMERGENCY_SOC] = 50
    result = await hass.config_entries.flow.async_configure(flow["flow_id"], user_input)
    assert result["type"] is data_entry_flow.FlowResultType.FORM
    assert result["errors"] == {"base": "invalid_installation"}


async def test_options_flow(hass, mock_config_entry) -> None:
    result = await hass.config_entries.options.async_init(mock_config_entry.entry_id)
    assert result["type"] is data_entry_flow.FlowResultType.FORM

    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        {
            CONF_OPERATING_MODE: OperatingMode.SHADOW,
            CONF_STRATEGY: Strategy.SAFE,
            CONF_DATA_SOURCE_MODE: DataSourceMode.HYBRID,
            CONF_UPDATE_INTERVAL: 120,
        },
    )
    assert result["type"] is data_entry_flow.FlowResultType.CREATE_ENTRY
    assert mock_config_entry.options[CONF_OPERATING_MODE] == OperatingMode.SHADOW


async def test_reconfigure_flow(hass, mock_config_entry, installation_data) -> None:
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={
            "source": config_entries.SOURCE_RECONFIGURE,
            "entry_id": mock_config_entry.entry_id,
        },
    )
    assert result["type"] is data_entry_flow.FlowResultType.FORM
    assert result["step_id"] == "reconfigure"

    installation_data["installation_name"] = "Renamed Energy System"
    installation_data["pv_peak_power_w"] = 8000
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], _flow_input(installation_data)
    )
    await hass.async_block_till_done()
    assert result["type"] is data_entry_flow.FlowResultType.ABORT
    assert result["reason"] == "reconfigure_successful"
    assert mock_config_entry.title == "Renamed Energy System"
    assert mock_config_entry.data["pv_peak_power_w"] == 8000
    assert await hass.config_entries.async_unload(mock_config_entry.entry_id)

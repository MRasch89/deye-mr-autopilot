"""Config flow for Deye MR Autopilot."""

from __future__ import annotations

from typing import Any
from uuid import uuid4

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.config_entries import ConfigFlowResult
from homeassistant.data_entry_flow import section
from homeassistant.helpers import selector

from .const import (
    CONF_BATTERY_CAPACITY_KWH,
    CONF_BATTERY_CHEMISTRY,
    CONF_BATTERY_USABLE_CAPACITY_KWH,
    CONF_DATA_SOURCE_MODE,
    CONF_EMERGENCY_SOC,
    CONF_INSTALLATION_NAME,
    CONF_INVERTER_MANUFACTURER,
    CONF_INVERTER_MODEL,
    CONF_INVERTER_POWER_W,
    CONF_MAX_CHARGE_POWER_W,
    CONF_MAX_DISCHARGE_POWER_W,
    CONF_MAXIMUM_SOC,
    CONF_MINIMUM_SOC,
    CONF_OPERATING_MODE,
    CONF_PV_PEAK_POWER_W,
    CONF_RECOVERY_SOC,
    CONF_STRATEGY,
    CONF_UPDATE_INTERVAL,
    DEFAULT_BATTERY_CAPACITY_KWH,
    DEFAULT_DATA_SOURCE_MODE,
    DEFAULT_EMERGENCY_SOC,
    DEFAULT_INVERTER_MANUFACTURER,
    DEFAULT_INVERTER_MODEL,
    DEFAULT_INVERTER_POWER_W,
    DEFAULT_MAX_CHARGE_POWER_W,
    DEFAULT_MAX_DISCHARGE_POWER_W,
    DEFAULT_MAXIMUM_SOC,
    DEFAULT_MINIMUM_SOC,
    DEFAULT_OPERATING_MODE,
    DEFAULT_PV_PEAK_POWER_W,
    DEFAULT_RECOVERY_SOC,
    DEFAULT_STRATEGY,
    DEFAULT_UPDATE_INTERVAL,
    DOMAIN,
    MAX_UPDATE_INTERVAL,
    MIN_UPDATE_INTERVAL,
    DataSourceMode,
    OperatingMode,
    Strategy,
)
from .models import InstallationConfig


def _number_selector(
    minimum: float, maximum: float, step: float, unit: str
) -> selector.NumberSelector:
    return selector.NumberSelector(
        selector.NumberSelectorConfig(
            min=minimum,
            max=maximum,
            step=step,
            mode=selector.NumberSelectorMode.BOX,
            unit_of_measurement=unit,
        )
    )


def _installation_schema(defaults: dict[str, Any]) -> vol.Schema:
    """Build the installation schema with supplied defaults."""
    usable_capacity = defaults.get(CONF_BATTERY_USABLE_CAPACITY_KWH)
    usable_capacity_field = (
        vol.Optional(
            CONF_BATTERY_USABLE_CAPACITY_KWH,
            default=usable_capacity,
        )
        if usable_capacity not in (None, "")
        else vol.Optional(CONF_BATTERY_USABLE_CAPACITY_KWH)
    )
    return vol.Schema(
        {
            vol.Required(
                CONF_INSTALLATION_NAME,
                default=defaults.get(CONF_INSTALLATION_NAME, "Home Energy System"),
            ): selector.TextSelector(),
            vol.Required(
                CONF_INVERTER_MANUFACTURER,
                default=defaults.get(
                    CONF_INVERTER_MANUFACTURER, DEFAULT_INVERTER_MANUFACTURER
                ),
            ): selector.TextSelector(),
            vol.Required(
                CONF_INVERTER_MODEL,
                default=defaults.get(CONF_INVERTER_MODEL, DEFAULT_INVERTER_MODEL),
            ): selector.TextSelector(),
            vol.Required(
                CONF_INVERTER_POWER_W,
                default=defaults.get(CONF_INVERTER_POWER_W, DEFAULT_INVERTER_POWER_W),
            ): _number_selector(100, 100000, 100, "W"),
            vol.Required(
                CONF_PV_PEAK_POWER_W,
                default=defaults.get(CONF_PV_PEAK_POWER_W, DEFAULT_PV_PEAK_POWER_W),
            ): _number_selector(100, 200000, 100, "W"),
            vol.Required(
                CONF_BATTERY_CAPACITY_KWH,
                default=defaults.get(
                    CONF_BATTERY_CAPACITY_KWH, DEFAULT_BATTERY_CAPACITY_KWH
                ),
            ): _number_selector(0.1, 1000, 0.1, "kWh"),
            usable_capacity_field: _number_selector(0.1, 1000, 0.1, "kWh"),
            vol.Optional(
                CONF_BATTERY_CHEMISTRY,
                default=defaults.get(CONF_BATTERY_CHEMISTRY, ""),
            ): selector.TextSelector(),
            vol.Required(
                CONF_MAX_CHARGE_POWER_W,
                default=defaults.get(
                    CONF_MAX_CHARGE_POWER_W, DEFAULT_MAX_CHARGE_POWER_W
                ),
            ): _number_selector(100, 100000, 100, "W"),
            vol.Required(
                CONF_MAX_DISCHARGE_POWER_W,
                default=defaults.get(
                    CONF_MAX_DISCHARGE_POWER_W, DEFAULT_MAX_DISCHARGE_POWER_W
                ),
            ): _number_selector(100, 100000, 100, "W"),
            vol.Required("soc_limits"): section(
                vol.Schema(
                    {
                        vol.Required(
                            CONF_EMERGENCY_SOC,
                            default=defaults.get(
                                CONF_EMERGENCY_SOC, DEFAULT_EMERGENCY_SOC
                            ),
                        ): _number_selector(0, 100, 1, "%"),
                        vol.Required(
                            CONF_MINIMUM_SOC,
                            default=defaults.get(CONF_MINIMUM_SOC, DEFAULT_MINIMUM_SOC),
                        ): _number_selector(0, 100, 1, "%"),
                        vol.Required(
                            CONF_RECOVERY_SOC,
                            default=defaults.get(
                                CONF_RECOVERY_SOC, DEFAULT_RECOVERY_SOC
                            ),
                        ): _number_selector(0, 100, 1, "%"),
                        vol.Required(
                            CONF_MAXIMUM_SOC,
                            default=defaults.get(CONF_MAXIMUM_SOC, DEFAULT_MAXIMUM_SOC),
                        ): _number_selector(0, 100, 1, "%"),
                    }
                ),
                {"collapsed": False},
            ),
        }
    )


def _flatten_sections(user_input: dict[str, Any]) -> dict[str, Any]:
    """Flatten section data before persisting it."""
    flattened = dict(user_input)
    soc_limits = flattened.pop("soc_limits", {})
    flattened.update(soc_limits)
    return flattened


def _options_schema(options: dict[str, Any]) -> vol.Schema:
    return vol.Schema(
        {
            vol.Required(
                CONF_OPERATING_MODE,
                default=options.get(CONF_OPERATING_MODE, DEFAULT_OPERATING_MODE),
            ): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=[mode.value for mode in OperatingMode],
                    translation_key="operating_mode",
                )
            ),
            vol.Required(
                CONF_STRATEGY,
                default=options.get(CONF_STRATEGY, DEFAULT_STRATEGY),
            ): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=[strategy.value for strategy in Strategy],
                    translation_key="strategy",
                )
            ),
            vol.Required(
                CONF_DATA_SOURCE_MODE,
                default=options.get(CONF_DATA_SOURCE_MODE, DEFAULT_DATA_SOURCE_MODE),
            ): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=[source.value for source in DataSourceMode],
                    translation_key="data_source_mode",
                )
            ),
            vol.Required(
                CONF_UPDATE_INTERVAL,
                default=options.get(CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL),
            ): _number_selector(MIN_UPDATE_INTERVAL, MAX_UPDATE_INTERVAL, 1, "s"),
        }
    )


class DeyeMRAutopilotConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle the Deye MR Autopilot configuration flow."""

    VERSION = 1
    MINOR_VERSION = 1

    @staticmethod
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> DeyeMRAutopilotOptionsFlow:
        return DeyeMRAutopilotOptionsFlow()

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            data = _flatten_sections(user_input)
            try:
                config = InstallationConfig.from_mapping(data)
            except KeyError, TypeError, ValueError:
                errors["base"] = "invalid_installation"
            else:
                await self.async_set_unique_id(str(uuid4()))
                return self.async_create_entry(title=config.name, data=data)

        return self.async_show_form(
            step_id="user",
            data_schema=_installation_schema(user_input or {}),
            errors=errors,
        )

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        entry = self._get_reconfigure_entry()
        errors: dict[str, str] = {}
        if user_input is not None:
            data = _flatten_sections(user_input)
            try:
                config = InstallationConfig.from_mapping(data)
            except KeyError, TypeError, ValueError:
                errors["base"] = "invalid_installation"
            else:
                return self.async_update_reload_and_abort(
                    entry,
                    title=config.name,
                    data=data,
                )

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=_installation_schema(user_input or dict(entry.data)),
            errors=errors,
        )


class DeyeMRAutopilotOptionsFlow(config_entries.OptionsFlow):
    """Handle optional runtime settings."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        if user_input is not None:
            return self.async_create_entry(data=user_input)
        return self.async_show_form(
            step_id="init",
            data_schema=_options_schema(dict(self.config_entry.options)),
        )

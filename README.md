# Deye MR Autopilot

[![Version](https://img.shields.io/badge/version-0.1.0--alpha.2-orange)](https://github.com/MRasch89/deye-mr-autopilot/releases)
[![Home Assistant](https://img.shields.io/badge/Home%20Assistant-2026.8%2B-41BDF5)](https://www.home-assistant.io/)
[![License](https://img.shields.io/badge/license-Apache--2.0-blue)](LICENSE)

Deye MR Autopilot is a Home Assistant-native, local-first foundation for a safe,
explainable Home Energy Management System for hybrid solar installations. It is
designed to observe, forecast, recommend, simulate, verify, and only then control.

> **Development status:** Phase 0 and Phase 1 alpha. This release does not read an
> inverter, write Modbus registers, or perform physical control. The arming switch
> deliberately refuses to turn on.

## What it is

- A HACS-installable custom integration running entirely inside Home Assistant.
- A modular architecture for entity mapping, forecasts, consumption learning,
  optimization, deterministic agent decisions, safety, and verified control.
- Local-first: no project telemetry, account, backend, database, or cloud runtime.
- Fail-safe: optional components sit behind interfaces and cannot bypass safety.

## What it is not

It is not a Home Assistant add-on, Docker service, web backend, MQTT broker, external
agent server, EMHASS deployment, or a replacement for an existing Deye/Solarman
monitoring integration. No arbitrary register-write action will be provided.

## Current entities

- `sensor`: Status, Safety status
- `select`: Autopilot mode, Strategy
- `switch`: Control armed (visible but hard-blocked in Phase 1)

The safe defaults are `MONITOR`, `BALANCED`, and control disarmed.

## Installation through HACS

1. Publish this repository on GitHub and create release `0.1.0-alpha.1`.
2. In HACS, open **Integrations**, then the menu and **Custom repositories**.
3. Enter the GitHub repository URL, choose **Integration**, and add it.
4. Install **Deye MR Autopilot** and restart Home Assistant.
5. Open **Settings → Devices & services → Add integration**.
6. Search for **Deye MR Autopilot** and complete the form.

Manual development installation is also possible by copying
`custom_components/deye_mr_autopilot` into Home Assistant's `custom_components`
directory and restarting Home Assistant.

## Configuration

The GUI flow records the installation name, inverter identity and nominal power, PV
peak power, battery capacities, SOC safety limits, and charge/discharge power limits.
Options expose the operating mode, strategy, future data-source topology, and status
update interval. Reconfiguration is supported from the config-entry menu.

The initial Deye SUN-6K-SG05LP3-EU and 15 kWh values are only editable defaults. They
are never embedded into decision logic.

## Safety

The required command path is:

`Decision → Safety Engine → Control Adapter → Write → Read-back verification`

Phase 1 stops at the safety engine. The model-specific register allowlist is empty.
Unknown profiles and unknown actions cannot write. See [SAFETY.md](SAFETY.md).

## Development

See [ARCHITECTURE.md](ARCHITECTURE.md), [DEVELOPMENT.md](DEVELOPMENT.md), and
[ROADMAP.md](ROADMAP.md). The next development milestone is the read-only entity
data layer described under Phase 2.

## Known limitations

- No Home Assistant source-entity mapping or unit normalization yet.
- No installation snapshot, forecasts, weather, battery model, or learning yet.
- The optimizer and agent graph are deliberately safe skeletons.
- LangGraph and `pysolarmanv5` are compatibility-tested but optional and unbundled.
- No verified Deye writable-register profile exists.
- Repository owner URLs and `codeowners` must be set to the actual GitHub account
  before the first public release.

## Privacy

Deye MR Autopilot sends no analytics or telemetry. Future forecast and weather input
will primarily consume data already present in Home Assistant.

## License

Apache License 2.0.

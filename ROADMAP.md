# Roadmap

## Complete: Phase 0 — feasibility

- Reviewed current Home Assistant and HACS requirements.
- Targeted Home Assistant 2026.8 / Python 3.14.2+.
- Verified LangGraph and pysolarmanv5 resolution/import on CPython 3.14.
- Kept both optional and excluded EMHASS.

## Complete: Phase 1 — safe integration skeleton

- GUI config, reconfigure, and options flows.
- Logical device and initial status/control entities.
- Coordinator, diagnostics, Repair helper, translations, HACS metadata, CI.
- Provider interfaces, native graph, optional LangGraph graph, fallback optimizer,
  mock adapter, strict empty profile registry, and all-blocking safety engine.

## In progress: Phase 2 — entity data layer

Completed in the first read-only increment:

- Immutable normalized telemetry snapshot.
- Deye/Solarman preset for core power, SOC, temperature, and daily energy entities.
- Connection, battery alarm, and battery fault observation.
- Missing, unavailable, invalid-unit, and stale-source tracking.
- Read-only normalized sensors and diagnostic source mapping.
- Tests proving that the collector only consumes Home Assistant states.

Remaining work:

1. Add entity selectors for every required and optional installation measurement.
2. Validate entity existence, state class, device class, and supported units.
3. Implement explicit W/kW/MW and Wh/kWh/MWh normalization with unit-change defense.
4. Expand per-field timestamps and physically plausible value validation.
5. Extend quality scoring with installation-specific bounds.
6. Consider state-change subscriptions while retaining bounded coordinator updates.
7. Add reconfigure migration for entity mappings and safe missing-entity Repairs.
8. Redact mapped sensitive identifiers where appropriate in diagnostics.
9. Add tests for mappings, unavailable/unknown states, stale data, unit changes,
   impossible values, sign conventions, reload, and storage migration.
10. Add simulation providers and fixtures for snapshot-only full-day tests.

Later phases add forecasts/weather, battery reserve, consumption learning, native MPC,
agent decisions, recommendation, shadow evaluation, and only then read-only Solarman and
model-verified control.

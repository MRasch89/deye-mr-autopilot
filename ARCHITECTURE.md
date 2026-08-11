# Architecture

## Phase 0 conclusions (2026-08-11)

The implementation targets Home Assistant Core 2026.8. Home Assistant Core 2026.8.1
declares Python `>=3.14.2`; compatibility checks were executed locally with CPython
3.14.3. The minimum version in `hacs.json` is therefore 2026.8.0.

Authoritative references reviewed:

- [Home Assistant integration manifest](https://developers.home-assistant.io/docs/creating_integration_manifest/)
- [Config flow and reconfigure flow](https://developers.home-assistant.io/docs/core/integration/config_flow/)
- [Options flow](https://developers.home-assistant.io/docs/core/integration/options_flow/)
- [Fetching data and DataUpdateCoordinator](https://developers.home-assistant.io/docs/integration_fetching_data/)
- [Device registry](https://developers.home-assistant.io/docs/device_registry_index/)
- [Integration quality scale](https://developers.home-assistant.io/docs/core/integration-quality-scale/)
- [Custom integration localization](https://developers.home-assistant.io/docs/internationalization/custom_integration/)
- [Diagnostics](https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/diagnostics/)
- [Repairs](https://developers.home-assistant.io/docs/core/platform/repairs/)
- [Home Assistant 2026.8.1 storage helper source](https://github.com/home-assistant/core/blob/2026.8.1/homeassistant/helpers/storage.py)
- [HACS integration publishing requirements](https://hacs.xyz/docs/publish/integration/)
- [HACS repository manifest](https://hacs.xyz/docs/publish/start/)

Current standards materially affecting the design:

- Config entries own configuration and runtime objects use `ConfigEntry.runtime_data`.
- Required setup data is changed through reconfigure; optional behavior uses options.
- Coordinator entities share one bounded update source and avoid per-entity polling.
- The Autopilot logical service owns its device; it does not merge with another
  integration's inverter device (Home Assistant 2026.8 single-entry device ownership).
- Entity names, flow labels, and selector choices use translation keys.
- Custom integrations ship complete `translations/en.json` and locale files; the Core-only
  `strings.json` build artifact is intentionally not used.
- HACS expects one integration below `custom_components`, root `hacs.json`, a versioned
  custom manifest, public GitHub metadata, a README, and a brand `icon.png`.

## Dependency gate

| Package | Tested version | Python 3.14 result | Phase 1 decision |
|---|---:|---|---|
| Home Assistant | 2026.8.1 | Requires Python >=3.14.2 | Test/runtime API baseline |
| LangGraph | 1.2.11 | Resolved and imported; basic graph API available | Optional lazy adapter only |
| pysolarmanv5 | 3.0.6 | Resolved and imported; sync and async classes available | Not a runtime requirement yet |
| EMHASS | Not installed | Deliberately not tested/installed | Future provider interface only |

Both optional packages report MIT licensing. LangGraph brings a much larger transitive
dependency tree (LangChain Core, Pydantic, checkpoint, SDK, HTTP, serialization
packages). Making that tree mandatory would contradict graceful degradation in this
early phase. `pysolarmanv5` is small but will not be shipped until read-only direct
communication is implemented and tested on relevant Home Assistant architectures.

The compatibility check proves package resolution and import on Windows x86-64. It is
not evidence of logger communication, register correctness, or wheel availability on
every Home Assistant hardware architecture. CI maintains Python compatibility; later
phases must add architecture-specific installation evidence.

## Runtime boundaries

```text
Home Assistant config entries and entities
              │
              ▼
InstallationConfig / future InstallationSnapshot
              │
       ForecastProvider + WeatherProvider
              │
              ▼
       OptimizationProvider
              │
              ▼
      AgentGraph (native always available,
       LangGraph optional and in-process)
              │
              ▼
          Decision intent
              │
              ▼
        SafetyEngine (final authority)
              │
              ▼
    ControlAdapter (high-level allowlist only)
              │
              ▼
       write → read-back → evaluation
```

Business models and contracts live in small Python modules. Home Assistant adapters
remain at the boundary so forecasting, battery, optimization, and safety algorithms can
be tested without Home Assistant hardware.

## Phase 1 runtime

`async_setup_entry` validates stored installation data, creates the logical service
device, constructs entry-scoped dependencies, performs a first coordinator refresh,
and forwards sensor/select/switch platforms. Entry options reload the entry.

The coordinator performs no inverter I/O. It exposes only a comparable status model at
a bounded interval. The SafeFallbackOptimizer emits one `NO_ACTION` point. The native
agent graph marks absent installation data invalid and emits `NO_ACTION`. The Phase 1
SafetyEngine rejects all commands. The only active adapter is MockControlAdapter.

`LangGraphAgentGraph` is implemented behind the same interface and imports LangGraph
only when explicitly instantiated and installed. The integration manifest has no
runtime requirements, so missing optional modules cannot prevent Home Assistant setup.

## Configuration ownership

Config-entry data contains installation facts and hard safety limits. Options contain
runtime behavior: operating mode, strategy, data-source topology, and coordinator
interval. AUTOPILOT mode and control arming remain separate states. Control arming is
non-persistent and always false in Phase 1.

## Future storage

Learning, compact decision summaries, and model state will use versioned Home Assistant
`Store` objects with retention limits. Recorder remains responsible for ordinary entity
history. No external database or unbounded event history will be introduced.

# Safety model

Safety is a hard architectural boundary, not an optimizer preference.

## Phase 1 guarantees

- Physical control is not implemented or armed.
- `manifest.json` has no Solarman or Modbus dependency.
- The SafetyEngine rejects every command.
- The active MockControlAdapter performs no network or entity I/O.
- SolarmanControlAdapter and EntityControlAdapter are disabled placeholders.
- The inverter profile registry is empty.
- There is no public raw-register API or Home Assistant action.
- Selecting AUTOPILOT cannot enable a write path.
- Restarting Home Assistant leaves control disarmed.

## Required future execution sequence

1. Create a typed high-level decision.
2. Translate it to an allowlisted model-specific command.
3. Validate current data age, SOC, limits, capabilities, cooldown, and hysteresis.
4. Obtain explicit SafetyEngine approval.
5. Write once through the selected ControlAdapter.
6. Wait a bounded verification interval.
7. Read back through the same model profile.
8. Compare expected and observed state.
9. Record success or failure and apply cooldown.
10. Disarm and raise a Repair issue after repeated verification failures.

Any missing data, unknown profile, unknown action, stale state, failed connection,
unexpected read-back, or safety exception produces `NO_ACTION`.

## Registers

No writable Deye register address is present in this repository. Future register work
must cite reliable model-specific evidence for the exact inverter family, include scale,
type, bounds, write function, and read-back behavior, and pass MockControlAdapter tests
before hardware testing. Addresses are never inferred from another Deye family.

## Reporting safety issues

Do not publish inverter credentials, serial numbers, IP addresses, diagnostic exports,
or register dumps containing private installation information. Use the security policy
for vulnerabilities and the issue tracker for non-sensitive safety defects.


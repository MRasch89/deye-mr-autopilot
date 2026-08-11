## Summary

Describe the user-visible outcome and architectural boundary affected.

## Safety checklist

- [ ] No component bypasses SafetyEngine and ControlAdapter.
- [ ] No raw or unverified register write is exposed.
- [ ] Missing/stale/invalid data produces a safe result.
- [ ] Optional dependency failure does not break core monitoring.
- [ ] New behavior has automated tests.
- [ ] English and Polish translations are updated where needed.

## Validation

List tests, Ruff, HACS, and Hassfest results.


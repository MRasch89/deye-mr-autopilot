# Development

## Prerequisites

- CPython 3.14.2 or newer in the 3.14 series
- Git
- A current Home Assistant test environment

On Windows:

```powershell
py -3.14 -m venv .venv
.venv\Scripts\python -m pip install --upgrade pip
.venv\Scripts\python -m pip install -e ".[test]"
.venv\Scripts\python scripts\run_tests_windows.py -q --cov
.venv\Scripts\python -m ruff check .
.venv\Scripts\python -m ruff format --check .
```

Home Assistant itself targets Unix hosts. The Windows helper applies process-local
import and asyncio socket shims solely to its test harness. GitHub Actions runs plain
`pytest` on Linux with the official socket guard unchanged.

## Design rules

- Keep business logic independent from Home Assistant where practical.
- Use async Home Assistant APIs; move bounded CPU work to the executor if required.
- Add no mandatory dependency without documenting Python, wheel, license, size, event
  loop, and failure-mode compatibility.
- Never add a generic register-write service or leak a register API above Solarman.
- Preserve MONITOR as the first-install default and explicit separate arming.
- Every failure path must remain useful for monitoring and safe for control.

## Pull requests

Run tests, Ruff, JSON parsing, HACS validation, and Hassfest. Add or update tests for
every safety behavior. Do not lower validation coverage to merge a hardware feature.

## Release checklist

1. Replace repository-owner placeholders in manifest URLs and `CODEOWNERS`.
2. Run test and validation workflows.
3. Confirm `manifest.json` and release tag versions agree.
4. Publish a GitHub release (a tag alone is insufficient for the planned workflow).
5. Install the release through HACS in a clean Home Assistant instance.
6. Confirm the config, options, and reconfigure flows in English and Polish.
7. Confirm control is disarmed after setup, reload, and restart.

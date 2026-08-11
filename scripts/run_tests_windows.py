"""Run the Home Assistant test harness on Windows for local development.

Home Assistant 2026.8 targets Unix hosts and imports ``fcntl`` and ``resource``.
Its pytest socket guard also blocks the loopback socket pair used by Windows asyncio.
This process-local shim supplies only the import-time APIs and disables that socket
guard. CI runs on Linux with the unmodified official harness.
"""

from __future__ import annotations

import sys
from types import ModuleType


def _install_unix_import_shims() -> None:
    fcntl = ModuleType("fcntl")
    fcntl.LOCK_EX = 2  # type: ignore[attr-defined]
    fcntl.LOCK_NB = 4  # type: ignore[attr-defined]
    fcntl.flock = lambda *_args: None  # type: ignore[attr-defined]
    sys.modules["fcntl"] = fcntl

    resource = ModuleType("resource")
    resource.RLIMIT_NOFILE = 7  # type: ignore[attr-defined]
    resource.getrlimit = lambda *_args: (2048, 2048)  # type: ignore[attr-defined]
    resource.setrlimit = lambda *_args: None  # type: ignore[attr-defined]
    sys.modules["resource"] = resource


def main() -> int:
    """Run pytest with Windows-only process shims."""
    _install_unix_import_shims()

    import pytest
    import pytest_socket

    pytest_socket.disable_socket = lambda *_args, **_kwargs: None
    pytest_socket.socket_allow_hosts = lambda *_args, **_kwargs: None
    return pytest.main(sys.argv[1:] or ["-q"])


if __name__ == "__main__":
    raise SystemExit(main())

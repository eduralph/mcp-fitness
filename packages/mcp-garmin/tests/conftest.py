"""Pytest config for mcp-garmin tests."""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

import pytest
import structlog

if TYPE_CHECKING:
    from collections.abc import Iterator


@pytest.fixture(autouse=True)
def _clear_mcp_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Strip MCP_* env vars from the test process."""
    for key in [k for k in os.environ if k.startswith("MCP_")]:
        monkeypatch.delenv(key, raising=False)


@pytest.fixture(autouse=True)
def _reset_structlog() -> Iterator[None]:
    """Reset structlog state so the configure_logging call inside
    build_server() / main() doesn't leak between tests."""
    structlog.reset_defaults()
    yield
    structlog.reset_defaults()

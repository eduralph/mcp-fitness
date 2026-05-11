"""Shared pytest configuration for mcp-fitness-shared tests."""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

import pytest
import structlog

if TYPE_CHECKING:
    from collections.abc import Iterator


@pytest.fixture(autouse=True)
def _clear_mcp_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Strip ``MCP_*`` env vars from the test process so SharedSettings is hermetic."""
    for key in [k for k in os.environ if k.startswith("MCP_")]:
        monkeypatch.delenv(key, raising=False)


@pytest.fixture(autouse=True)
def _reset_structlog() -> Iterator[None]:
    """Reset structlog config + logger cache so tests don't bleed state."""
    structlog.reset_defaults()
    yield
    structlog.reset_defaults()

"""Tests for mcp_fitness_shared.config."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from mcp_fitness_shared.config import SharedSettings

if TYPE_CHECKING:
    import pytest


def test_defaults() -> None:
    s = SharedSettings()
    assert s.host == "0.0.0.0"
    assert s.port == 8080
    assert s.log_level == "INFO"
    assert s.token_dir == Path("/data/tokens")


def test_env_overrides(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("MCP_HOST", "127.0.0.1")
    monkeypatch.setenv("MCP_PORT", "9090")
    monkeypatch.setenv("MCP_LOG_LEVEL", "DEBUG")
    monkeypatch.setenv("MCP_TOKEN_DIR", str(tmp_path))
    s = SharedSettings()
    assert s.host == "127.0.0.1"
    assert s.port == 9090
    assert s.log_level == "DEBUG"
    assert s.token_dir == tmp_path


def test_kwargs_for_tests(tmp_path: Path) -> None:
    """populate_by_name=True allows tests to pass values directly."""
    s = SharedSettings(host="1.2.3.4", port=1234, log_level="WARNING", token_dir=tmp_path)
    assert s.host == "1.2.3.4"
    assert s.port == 1234
    assert s.log_level == "WARNING"
    assert s.token_dir == tmp_path


def test_extra_env_ignored(monkeypatch: pytest.MonkeyPatch) -> None:
    """MCP_STRYD_* and friends must not break SharedSettings construction."""
    monkeypatch.setenv("MCP_STRYD_CLIENT_ID", "abc")
    monkeypatch.setenv("MCP_GARMIN_FIT_DIR", "/wherever")
    SharedSettings()  # must not raise

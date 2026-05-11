"""Tests for the ``python -m mcp_stryd`` entry point.

``FastMCP.run`` blocks forever in production. We stub it out and assert
the entry point reads settings from the environment and forwards them
into ``run`` correctly.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import fastmcp

from mcp_stryd.__main__ import main

if TYPE_CHECKING:
    from pathlib import Path

    import pytest


def test_main_wires_env_into_fastmcp_run(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("MCP_HOST", "127.0.0.99")
    monkeypatch.setenv("MCP_PORT", "9999")
    monkeypatch.setenv("MCP_LOG_LEVEL", "WARNING")
    monkeypatch.setenv("MCP_TOKEN_DIR", str(tmp_path))

    captured: dict[str, Any] = {}

    def fake_run(self: fastmcp.FastMCP, **kwargs: Any) -> None:
        captured["self_name"] = self.name
        captured["kwargs"] = kwargs

    monkeypatch.setattr(fastmcp.FastMCP, "run", fake_run)

    main()

    assert captured["self_name"] == "mcp-stryd"
    kwargs = captured["kwargs"]
    assert kwargs["transport"] == "http"
    assert kwargs["host"] == "127.0.0.99"
    assert kwargs["port"] == 9999
    assert kwargs["log_level"] == "warning"  # lowercased for uvicorn
    assert kwargs["show_banner"] is False


def test_main_uses_shared_defaults_when_env_unset(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    # _clear_mcp_env autouse fixture already strips MCP_*; we only set
    # token_dir so a stray /data/tokens write attempt can't happen.
    monkeypatch.setenv("MCP_TOKEN_DIR", str(tmp_path))

    captured: dict[str, Any] = {}

    def fake_run(self: fastmcp.FastMCP, **kwargs: Any) -> None:
        captured.update(kwargs)

    monkeypatch.setattr(fastmcp.FastMCP, "run", fake_run)

    main()

    assert captured["host"] == "0.0.0.0"  # the documented default
    assert captured["port"] == 8080
    assert captured["log_level"] == "info"

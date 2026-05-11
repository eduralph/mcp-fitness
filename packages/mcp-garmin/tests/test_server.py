"""Smoke tests for the mcp-garmin server."""

from __future__ import annotations

from typing import TYPE_CHECKING

import httpx
from fastmcp import Client

from mcp_garmin import __version__
from mcp_garmin.config import GarminSettings
from mcp_garmin.server import SERVICE_NAME, build_server

if TYPE_CHECKING:
    from pathlib import Path


def _settings(tmp_path: Path) -> GarminSettings:
    return GarminSettings(token_dir=tmp_path, log_level="WARNING")


async def test_server_exposes_health_tool(tmp_path: Path) -> None:
    mcp = build_server(_settings(tmp_path))
    async with Client(mcp) as client:
        tools = await client.list_tools()
        names = [t.name for t in tools]
        assert "health" in names
        result = await client.call_tool("health", {})
    payload = result.structured_content
    assert payload == {
        "status": "ok",
        "service": SERVICE_NAME,
        "version": __version__,
        "providers": {},
    }
    assert result.data.status == "ok"
    assert result.data.service == SERVICE_NAME


async def test_server_serves_health_http_route(tmp_path: Path) -> None:
    mcp = build_server(_settings(tmp_path))
    app = mcp.http_app()
    async with (
        app.router.lifespan_context(app),
        httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client,
    ):
        resp = await client.get("/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body == {
        "status": "ok",
        "service": SERVICE_NAME,
        "version": __version__,
        "providers": {},
    }


async def test_garmin_settings_inherits_shared_defaults() -> None:
    s = GarminSettings()
    assert s.host == "0.0.0.0"
    assert s.port == 8080
    assert s.log_level == "INFO"

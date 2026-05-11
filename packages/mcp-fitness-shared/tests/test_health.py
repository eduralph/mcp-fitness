"""Tests for the /health endpoint factory and HealthStatus model."""

from __future__ import annotations

from typing import TYPE_CHECKING

import httpx
import pytest
from fastmcp import FastMCP

from mcp_fitness_shared.health import (
    HealthStatus,
    build_health_status,
    register_health_endpoint,
)

if TYPE_CHECKING:
    from collections.abc import Mapping


async def test_build_status_no_providers() -> None:
    status = await build_health_status(
        service_name="mcp-test", version="0.1.0", check_providers=None
    )
    assert status == HealthStatus(status="ok", service="mcp-test", version="0.1.0", providers={})


async def test_build_status_all_ok() -> None:
    async def check() -> Mapping[str, str]:
        return {"a": "ok", "b": "ok"}

    status = await build_health_status(
        service_name="mcp-test", version="0.1.0", check_providers=check
    )
    assert status.status == "ok"
    assert status.providers == {"a": "ok", "b": "ok"}


async def test_build_status_degraded_when_any_unhealthy() -> None:
    async def check() -> Mapping[str, str]:
        return {"a": "ok", "b": "auth_required"}

    status = await build_health_status(
        service_name="mcp-test", version="0.1.0", check_providers=check
    )
    assert status.status == "degraded"
    assert status.providers["b"] == "auth_required"


async def test_build_status_degrades_when_check_raises() -> None:
    """A check_providers that raises must not crash /health — it must
    surface as a synthetic _check_error provider entry and a 503."""

    async def check() -> Mapping[str, str]:
        raise RuntimeError("upstream timeout")

    status = await build_health_status(
        service_name="mcp-test", version="0.1.0", check_providers=check
    )
    assert status.status == "degraded"
    assert "_check_error" in status.providers
    assert "RuntimeError" in status.providers["_check_error"]
    assert "upstream timeout" in status.providers["_check_error"]


async def test_endpoint_returns_503_when_check_raises() -> None:
    """The HTTP-level integration of the same invariant."""

    async def check() -> Mapping[str, str]:
        raise RuntimeError("upstream timeout")

    mcp: FastMCP = FastMCP("mcp-test")
    register_health_endpoint(mcp, service_name="mcp-test", version="0.1.0", check_providers=check)
    resp = await _get_health(mcp)
    assert resp.status_code == 503
    body = resp.json()
    assert body["status"] == "degraded"
    assert "_check_error" in body["providers"]


async def _get_health(mcp: FastMCP) -> httpx.Response:
    app = mcp.http_app()
    transport = httpx.ASGITransport(app=app)
    async with (
        app.router.lifespan_context(app),
        httpx.AsyncClient(transport=transport, base_url="http://test") as client,
    ):
        return await client.get("/health")


async def test_endpoint_returns_200_when_ok() -> None:
    mcp: FastMCP = FastMCP("mcp-test")
    register_health_endpoint(mcp, service_name="mcp-test", version="9.9.9")
    resp = await _get_health(mcp)
    assert resp.status_code == 200
    body = resp.json()
    assert body == {
        "status": "ok",
        "service": "mcp-test",
        "version": "9.9.9",
        "providers": {},
    }


async def test_endpoint_returns_503_when_degraded() -> None:
    async def check() -> Mapping[str, str]:
        return {"upstream": "auth_required"}

    mcp: FastMCP = FastMCP("mcp-test")
    register_health_endpoint(mcp, service_name="mcp-test", version="0.1.0", check_providers=check)
    resp = await _get_health(mcp)
    assert resp.status_code == 503
    assert resp.json()["status"] == "degraded"
    assert resp.json()["providers"] == {"upstream": "auth_required"}


@pytest.mark.parametrize("status_value", ["ok", "degraded"])
def test_health_status_model_roundtrip(status_value: str) -> None:
    s = HealthStatus(status=status_value, service="x", version="1", providers={"p": "ok"})
    again = HealthStatus.model_validate(s.model_dump())
    assert again == s

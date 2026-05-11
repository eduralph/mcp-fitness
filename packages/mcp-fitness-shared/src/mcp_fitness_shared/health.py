"""``/health`` endpoint factory + matching tool model.

Every server in the monorepo exposes the same shape so external
monitoring (Docker healthcheck, Cloudflare Tunnel, manual ``curl``)
treats them uniformly.

Response shape::

    {
      "status": "ok" | "degraded",
      "service": "mcp-stryd",
      "version": "0.1.0",
      "providers": { "stryd": "ok", ... }
    }

Returns ``200`` when ``status == "ok"``, ``503`` when degraded — see
architecture.md §"Logging and observability".
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable, Mapping
from typing import TYPE_CHECKING

from pydantic import BaseModel, Field
from starlette.responses import JSONResponse

if TYPE_CHECKING:
    from fastmcp import FastMCP
    from starlette.requests import Request


ProviderCheck = Callable[[], Awaitable[Mapping[str, str]]]
"""Async callable returning a mapping of provider name → ``"ok"``/error string.

Phase 0 servers register no providers; the callable is optional.
"""


class HealthStatus(BaseModel):
    """Structured health payload — used for both the HTTP endpoint and the MCP tool."""

    status: str = Field(description="'ok' if all providers healthy, otherwise 'degraded'.")
    service: str = Field(description="Short server name, e.g. 'mcp-stryd'.")
    version: str = Field(description="Package version of the running server.")
    providers: dict[str, str] = Field(
        default_factory=dict,
        description="Provider name → 'ok' or a short error string.",
    )


# Synthetic provider key used when ``check_providers`` itself raises —
# never crashes the /health endpoint, but surfaces the failure cleanly
# so monitoring (Docker healthcheck, Cloudflare) sees a 503.
_CHECK_ERROR_KEY = "_check_error"


async def build_health_status(
    *,
    service_name: str,
    version: str,
    check_providers: ProviderCheck | None,
) -> HealthStatus:
    """Run provider checks (if any) and assemble a :class:`HealthStatus`.

    Resilient to ``check_providers`` raising — an exception there
    becomes a synthetic ``_check_error`` provider entry with the
    exception class name and message. The /health endpoint therefore
    never returns a 500, only 200 or 503. See
    ``docs/architecture.md`` §"Logging and observability".
    """
    providers: dict[str, str] = {}
    if check_providers is not None:
        try:
            result = await check_providers()
            providers = dict(result)
        except Exception as exc:
            # Intentional: surface as degraded, never crash.
            providers = {_CHECK_ERROR_KEY: f"{type(exc).__name__}: {exc}"}
    degraded = any(value != "ok" for value in providers.values())
    return HealthStatus(
        status="degraded" if degraded else "ok",
        service=service_name,
        version=version,
        providers=providers,
    )


def register_health_endpoint(
    mcp: FastMCP,
    *,
    service_name: str,
    version: str,
    check_providers: ProviderCheck | None = None,
) -> None:
    """Mount ``GET /health`` on the given FastMCP server.

    Idempotent only in the sense that calling it twice will register
    two routes — don't. Call once during server construction.
    """

    @mcp.custom_route("/health", methods=["GET"], name="health")
    async def health(_request: Request) -> JSONResponse:
        status = await build_health_status(
            service_name=service_name,
            version=version,
            check_providers=check_providers,
        )
        status_code = 200 if status.status == "ok" else 503
        return JSONResponse(status.model_dump(), status_code=status_code)

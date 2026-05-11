"""FastMCP server instance for mcp-garmin.

Phase 0 surface mirrors mcp-stryd: one ``health`` MCP tool and one
``GET /health`` HTTP route. No FIT parsing, no Connect calls.
"""

from __future__ import annotations

from fastmcp import FastMCP

from mcp_fitness_shared import (
    HealthStatus,
    build_health_status,
    configure_logging,
    get_logger,
    register_health_endpoint,
)
from mcp_garmin import __version__
from mcp_garmin.config import GarminSettings

SERVICE_NAME = "mcp-garmin"


def build_server(settings: GarminSettings | None = None) -> FastMCP:
    """Construct the FastMCP server.

    Logging is configured here as a side effect — the server is the
    single entry point, so it owns global setup. Tests pass a custom
    ``settings`` to keep that hermetic.
    """
    settings = settings or GarminSettings()
    configure_logging(level=settings.log_level)
    log = get_logger(__name__)
    log.info(
        "server_starting",
        service=SERVICE_NAME,
        version=__version__,
        host=settings.host,
        port=settings.port,
        token_dir=str(settings.token_dir),
    )

    mcp: FastMCP = FastMCP(name=SERVICE_NAME, version=__version__)

    @mcp.tool(
        name="health",
        description=(
            "Returns the server's current health status. Use this to verify "
            "the mcp-garmin server is reachable before invoking other tools."
        ),
    )
    async def health() -> HealthStatus:
        return await build_health_status(
            service_name=SERVICE_NAME,
            version=__version__,
            check_providers=None,
        )

    register_health_endpoint(mcp, service_name=SERVICE_NAME, version=__version__)
    return mcp

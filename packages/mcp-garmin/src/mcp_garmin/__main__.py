"""Entry point — ``python -m mcp_garmin`` or the ``mcp-garmin`` console script.

Uvicorn's access logger is disabled deliberately — see the analogous
note in :mod:`mcp_stryd.__main__`. Phase 2/3 endpoints will benefit
from the same protection; no path in this server should be appearing
in stdlib access logs that bypass the structlog PII chain.
"""

from __future__ import annotations

from mcp_garmin.config import GarminSettings
from mcp_garmin.server import build_server


def main() -> None:
    settings = GarminSettings()
    server = build_server(settings)
    server.run(
        transport="http",
        host=settings.host,
        port=settings.port,
        log_level=settings.log_level.lower(),
        show_banner=False,
        uvicorn_config={"access_log": False},
    )


if __name__ == "__main__":
    main()

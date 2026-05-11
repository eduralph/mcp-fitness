"""Entry point — ``python -m mcp_garmin`` or the ``mcp-garmin`` console script."""

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
    )


if __name__ == "__main__":
    main()

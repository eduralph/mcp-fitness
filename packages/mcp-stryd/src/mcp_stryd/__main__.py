"""Entry point — ``python -m mcp_stryd`` or the ``mcp-stryd`` console script.

Starts FastMCP's HTTP transport on the configured host and port. The
``http`` transport is what claude.ai talks to over the Cloudflare
Tunnel (see ``docs/architecture.md``); stdio is intentionally not
supported.
"""

from __future__ import annotations

from mcp_stryd.config import StrydSettings
from mcp_stryd.server import build_server


def main() -> None:
    settings = StrydSettings()
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

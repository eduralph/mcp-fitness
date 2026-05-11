"""Entry point — ``python -m mcp_stryd`` or the ``mcp-stryd`` console script.

Starts FastMCP's HTTP transport on the configured host and port. The
``http`` transport is what claude.ai talks to over the Cloudflare
Tunnel (see ``docs/architecture.md``); stdio is intentionally not
supported.

Uvicorn's access logger is disabled deliberately: access lines go to
stdlib logging, *not* through the structlog PII-redaction chain. Once
Phase 1 lands the OAuth callback (``/oauth/callback?code=…&state=…``)
those URL parameters would otherwise appear in cleartext stdout. The
``/health`` endpoint loses access logging too — Docker's healthcheck
and Cloudflare Tunnel don't need it.
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
        uvicorn_config={"access_log": False},
    )


if __name__ == "__main__":
    main()

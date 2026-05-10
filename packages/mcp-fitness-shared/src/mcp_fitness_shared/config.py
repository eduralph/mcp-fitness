"""Shared pydantic-settings base for every mcp-fitness server.

The four env vars below are common to all servers in this monorepo;
per-server settings (Stryd OAuth client ID, Garmin FIT dir, …) live in
each package's own ``config.py`` and extend :class:`SharedSettings`.

Why ``validation_alias`` instead of ``env_prefix``:
    Each server's package-level Settings class extends SharedSettings.
    If we used ``env_prefix="MCP_"`` here, a subclass setting
    ``env_prefix="MCP_STRYD_"`` would force the inherited fields to be
    read from ``MCP_STRYD_HOST`` etc. — but the architecture says these
    four are read from the unprefixed ``MCP_*`` names regardless of
    which server is reading them. Explicit aliases sidestep that.
"""

from __future__ import annotations

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class SharedSettings(BaseSettings):
    """Env-driven settings every server inherits.

    All fields can also be set positionally / by keyword for tests
    (``populate_by_name=True``).
    """

    model_config = SettingsConfigDict(
        extra="ignore",
        case_sensitive=False,
        populate_by_name=True,
        env_file=None,
    )

    host: str = Field(default="0.0.0.0", validation_alias="MCP_HOST")  # noqa: S104
    """Bind address inside the container. Default binds all interfaces."""

    port: int = Field(default=8080, validation_alias="MCP_PORT")
    """TCP port for the HTTP/SSE transport."""

    log_level: str = Field(default="INFO", validation_alias="MCP_LOG_LEVEL")
    """One of CRITICAL / ERROR / WARNING / INFO / DEBUG. Production runs at INFO."""

    token_dir: Path = Field(
        default=Path("/data/tokens"),
        validation_alias="MCP_TOKEN_DIR",
    )
    """Directory holding the on-disk token files (mode 0600). Mount as a Docker volume."""

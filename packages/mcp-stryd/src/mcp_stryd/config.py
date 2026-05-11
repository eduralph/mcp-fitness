"""Settings for the mcp-stryd server.

Phase 0: no Stryd-specific fields yet. Phase 1 will add
``MCP_STRYD_CLIENT_ID``, ``MCP_STRYD_CLIENT_SECRET``, and
``MCP_STRYD_REDIRECT_URI`` here — see ``docs/architecture.md``
§"Per-package configuration".
"""

from __future__ import annotations

from mcp_fitness_shared import SharedSettings


class StrydSettings(SharedSettings):
    """Stryd-server settings. Inherits the shared ``MCP_*`` vars unchanged."""

    # Phase 1 additions go here, each as a Field(..., validation_alias="MCP_STRYD_*").

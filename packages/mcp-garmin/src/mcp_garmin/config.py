"""Settings for the mcp-garmin server.

Phase 0: no Garmin-specific fields yet. Phase 2 will add
``MCP_GARMIN_FIT_DIR``; Phase 3 will add the opt-in
``MCP_GARMIN_CONNECT_*`` fields — see ``docs/architecture.md``
§"Per-package configuration".
"""

from __future__ import annotations

from mcp_fitness_shared import SharedSettings


class GarminSettings(SharedSettings):
    """Garmin-server settings. Inherits the shared ``MCP_*`` vars unchanged."""

    # Phase 2 / 3 additions go here, each as
    # Field(..., validation_alias="MCP_GARMIN_*").

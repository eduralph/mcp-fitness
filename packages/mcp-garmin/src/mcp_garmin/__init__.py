"""mcp-garmin — MCP server exposing Garmin activity data.

Phase 0: server boots, ``/health`` responds. FIT-file watcher lands in
Phase 2; opt-in Garmin Connect scraping lands in Phase 3.
"""

from __future__ import annotations

from importlib.metadata import version

# Resolved from installed package metadata so pyproject.toml is the
# single source of truth — bumping the wheel version alone is enough
# to update what ``/health`` reports.
__version__ = version("mcp-garmin")
__all__ = ["__version__"]

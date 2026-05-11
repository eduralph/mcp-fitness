"""mcp-garmin — MCP server exposing Garmin activity data.

Phase 0: server boots, ``/health`` responds. FIT-file watcher lands in
Phase 2; opt-in Garmin Connect scraping lands in Phase 3.
"""

from __future__ import annotations

__version__ = "0.1.0"
__all__ = ["__version__"]

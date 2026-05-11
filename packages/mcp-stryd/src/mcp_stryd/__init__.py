"""mcp-stryd — MCP server exposing Stryd training data.

Phase 0: server boots, ``/health`` responds. Stryd-specific tools land
in Phase 1; see :mod:`mcp_stryd.server` and ``docs/roadmap.md``.
"""

from __future__ import annotations

from importlib.metadata import version

# Resolved from installed package metadata so pyproject.toml is the
# single source of truth — bumping the wheel version alone is enough
# to update what ``/health`` reports.
__version__ = version("mcp-stryd")
__all__ = ["__version__"]

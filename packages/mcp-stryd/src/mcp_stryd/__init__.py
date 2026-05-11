"""mcp-stryd — MCP server exposing Stryd training data.

Phase 0: server boots, ``/health`` responds. Stryd-specific tools land
in Phase 1; see :mod:`mcp_stryd.server` and ``docs/roadmap.md``.
"""

from __future__ import annotations

__version__ = "0.1.0"
__all__ = ["__version__"]

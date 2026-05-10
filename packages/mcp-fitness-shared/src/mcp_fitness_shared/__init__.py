"""Shared utilities for the mcp-fitness monorepo (internal package).

Public surface:

- :class:`config.SharedSettings`
- :func:`logging.configure_logging`
- :func:`tokens.read_token_file`, :func:`tokens.write_token_file`
- :func:`health.register_health_endpoint`
"""

from __future__ import annotations

from mcp_fitness_shared.config import SharedSettings
from mcp_fitness_shared.health import HealthStatus, register_health_endpoint
from mcp_fitness_shared.logging import configure_logging, get_logger
from mcp_fitness_shared.tokens import read_token_file, write_token_file

__all__ = [
    "HealthStatus",
    "SharedSettings",
    "configure_logging",
    "get_logger",
    "read_token_file",
    "register_health_endpoint",
    "write_token_file",
]

__version__ = "0.1.0"

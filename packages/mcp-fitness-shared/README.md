# mcp-fitness-shared

**Internal package. Not published to PyPI.**

Shared utilities for the mcp-fitness servers:

- `config.SharedSettings` — pydantic-settings base with the env vars
  every server uses (`MCP_HOST`, `MCP_PORT`, `MCP_LOG_LEVEL`,
  `MCP_TOKEN_DIR`).
- `logging.configure_logging` — structlog setup with a PII redaction
  processor that scrubs `gps_lat`, `gps_lon`, `user_name`, `user_email`,
  `fit_user_field` from log records at `INFO` and above.
- `tokens.read_token_file` / `write_token_file` — atomic JSON r/w with
  mode `0600`. Used for OAuth and Connect tokens.
- `health.register_health_endpoint` — registers a `/health` HTTP route
  on a FastMCP instance.

Each public package (`mcp-stryd`, `mcp-garmin`) depends on this as a
path dependency. The wheel ships inside each public package's
distribution; downstream users never install this directly.

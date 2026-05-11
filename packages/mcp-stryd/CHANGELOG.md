# Changelog — mcp-stryd

All notable changes to **mcp-stryd** are documented here. The format
follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/);
versioning is [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [0.1.0] — initial scaffold

### Added

- FastMCP server skeleton with a single `health` tool returning a
  structured `HealthStatus`.
- `/health` HTTP endpoint mounted via the shared health-factory.
- `python -m mcp_stryd` entry point starting the HTTP/SSE transport.
- Path dependency on the internal `mcp-fitness-shared` package.
- `Dockerfile` (python:3.13-slim, non-root user) and per-package
  `docker-compose.example.yml`.
- Smoke tests covering the health tool and HTTP route via FastMCP's
  in-process `Client` and httpx `ASGITransport`.

### Out of scope (Phase 1 work)

- Stryd OAuth2 authorization flow and token persistence
- Async `httpx.AsyncClient` with retry / 401-refresh
- Tool implementations: `list_activities`, `get_activity`,
  `get_cp_history`, `get_training_balance`, `get_zones`

[Unreleased]: https://github.com/eduralph/mcp-fitness/compare/mcp-stryd-v0.1.0...HEAD
[0.1.0]: https://github.com/eduralph/mcp-fitness/releases/tag/mcp-stryd-v0.1.0

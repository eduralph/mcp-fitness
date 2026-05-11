# Changelog — mcp-garmin

All notable changes to **mcp-garmin** are documented here. The format
follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/);
versioning is [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [0.1.0] — initial scaffold

### Added

- FastMCP server skeleton with a single `health` tool returning a
  structured `HealthStatus`.
- `/health` HTTP endpoint mounted via the shared health-factory.
- `python -m mcp_garmin` entry point starting the HTTP/SSE transport.
- Path dependency on the internal `mcp-fitness-shared` package.
- `Dockerfile` (python:3.13-slim, non-root user) and per-package
  `docker-compose.example.yml`.
- Smoke tests covering the health tool and HTTP route via FastMCP's
  in-process `Client` and httpx `ASGITransport`.

### Out of scope (Phase 2 / 3 work)

- FIT-file folder watcher and parser (Phase 2)
- `list_fit_files`, `parse_fit` tools (Phase 2)
- Opt-in Garmin Connect client and `connect_*` tools (Phase 3)

[Unreleased]: https://github.com/eduralph/mcp-fitness/compare/mcp-garmin-v0.1.0...HEAD
[0.1.0]: https://github.com/eduralph/mcp-fitness/releases/tag/mcp-garmin-v0.1.0

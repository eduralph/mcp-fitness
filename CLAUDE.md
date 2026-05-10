# mcp-fitness — Claude Code conventions

This repo is **mcp-fitness**, an open-source monorepo containing two
independent MCP servers:

- **mcp-stryd** — reads Stryd power-based training data via Stryd's official API
- **mcp-garmin** — reads Garmin activities, primarily via FIT files auto-exported
  from the watch, with optional Garmin Connect scraping as a best-effort fallback

Author: Eduard Ralph (`eduralph` on GitHub). Sales engineer, 20+ years of
software development experience. Solo work, public from day one.

## Read these before changing anything substantive

- `docs/architecture.md` — server design, monorepo layout, deployment topology,
  tool inventories, config model. **Authoritative.**
- `docs/roadmap.md` — phased plan, current state, known risks, exit criteria.

Both are kept current as the project evolves. When something in the code
contradicts these docs, fix the doc or fix the code — don't leave the
contradiction.

## Tech stack (don't drift)

- Python 3.13 (Python 3.12 also supported in CI)
- FastMCP for the MCP server framework
- HTTP/SSE transport (NOT stdio; claude.ai requires remote MCP)
- `httpx` for async HTTP
- `pydantic-settings` for env-driven config
- `pydantic` for data models
- `pytest` + `pytest-asyncio` + `respx` for testing
- `ruff` for linting and formatting
- `mypy` strict mode for type checking
- GPL-3.0 license throughout

## Monorepo layout

```
packages/
├── mcp-fitness-shared/   # internal, never published to PyPI
├── mcp-stryd/            # public, published to PyPI + GHCR
└── mcp-garmin/           # public, published to PyPI + GHCR
```

`mcp-fitness-shared` provides: config base, structured logging with PII
redaction, atomic token file r/w, /health endpoint factory. Each public
package depends on it via path dependency in its pyproject.toml.

## Working style

- **Direct, technical output.** Skip introductory framing and recaps.
- **Diffs over descriptions.** When changing files, show the diff or
  the full new file — not prose about what changed.
- **Type hints everywhere.** mypy strict must pass.
- **Async by default** for I/O-bound work.
- **Structured logging.** No `print()`, no plain text logs.
- **PII redaction is enforced** in the shared logging module. INFO and
  above must never contain GPS coordinates, FIT user-field strings,
  user names, or emails. DEBUG can include more but never enabled in
  production.

## Configuration discipline

- All runtime config from env vars, parsed via `pydantic-settings`.
- Secrets read once at startup, never re-read. Restart the container
  to rotate.
- Token files live under `MCP_TOKEN_DIR` (a Docker volume), mode 0600,
  rewritten atomically.
- Never commit secrets. The repo contains `*.env.example` files only.

## Privacy boundary

Fitness data is **special-category personal data** under GDPR Art. 9.
This affects code conventions:

- Test fixtures: synthetic FIT files; recorded API responses with PII
  scrubbed. Never check in real exports.
- Logging at INFO+: no PII. Power numbers, paces, RSS scores, dates:
  ok. GPS, user names, emails, FIT user fields: not ok.
- The README must warn about this and document the privacy-relevant
  config (log levels, token directory permissions).

## Conventions for tests

- One test file per source module, named `test_<module>.py`.
- Fixtures live in `tests/fixtures/` per package.
- HTTP-talking code uses `respx` to mock; never hit real APIs in CI.
- FIT-parsing tests use hand-crafted synthetic FITs committed to fixtures.
- Tests must be hermetic — no network, no real filesystem outside `tmp_path`.

## Conventions for the MCP layer

- Use FastMCP decorators (`@mcp.tool`) for tool definitions.
- Type hints on tool functions determine the JSON schema exposed to
  the model — be precise.
- Tools return structured pydantic models, not free-form dicts.
- Errors are structured: `raise ToolError("code", "human message")`,
  not bare exceptions.
- Each server registers a `/health` endpoint via the shared health
  factory.

## Conventions for Docker

- Each public package has its own `Dockerfile` and
  `docker-compose.example.yml`.
- Base image: `python:3.13-slim`.
- Non-root user inside the container.
- Build context includes both the package and `mcp-fitness-shared`
  (path dependency).
- One image per published version, tagged on GitHub release.
- Repo-level `docker-compose.example.yml` shows both services deployed
  together; per-package examples show each in isolation.

## Conventions for releases

- Per-package semver, independent: `mcp-stryd-vX.Y.Z`,
  `mcp-garmin-vX.Y.Z`.
- Tag pattern triggers the matching GitHub Actions workflow.
- Each release publishes a PyPI wheel and a GHCR Docker image with
  matching version + `:latest` tag.
- `mcp-fitness-shared` never publishes — it travels inside each Docker
  image and inside each package's wheel via PEP 517 build hooks.

## What's intentionally NOT done

- No CLI client; the MCP protocol is the interface.
- No web UI; OAuth callback is the only direct HTTP-visible surface
  (besides /health and the MCP endpoint).
- No write-back to either provider — read-only.
- No real-time data during a workout; sessions are reviewed post hoc.
- No multi-tenancy; one user per deployment instance.
- No Strava / TrainingPeaks / Polar / COROS — extensible to those, but
  out of scope for now.

## When in doubt

Re-read `docs/architecture.md`. If the answer isn't there and isn't in
`docs/roadmap.md`, propose the answer in code and a doc update in the
same change.
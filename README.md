# mcp-fitness

Two independent [Model Context Protocol](https://modelcontextprotocol.io/)
servers that expose personal fitness data to Claude — one for
[Stryd](https://www.stryd.com/) power-based training data, one for
[Garmin](https://www.garmin.com/) activities (FIT files primarily; Garmin
Connect scraping as an opt-in fallback). Each server is its own package
with its own Dockerfile and version, sharing only a small internal
utilities layer (config, structured logging with PII redaction, atomic
token storage, health endpoint). Built around HTTP/SSE transport so it
works with `claude.ai` over a Cloudflare Tunnel — no stdio, no local-only
deployment.

## Packages

- **[mcp-stryd](packages/mcp-stryd/)** — Stryd activities, power curves,
  CP history, training balance, zones. Uses Stryd's official OAuth2 API.
- **[mcp-garmin](packages/mcp-garmin/)** — Garmin activities. FIT-file
  watcher is the primary, robust path; Garmin Connect scraping is opt-in
  and best-effort.
- **[mcp-fitness-shared](packages/mcp-fitness-shared/)** — internal-only,
  never published to PyPI. Ships inside each public package's Docker
  image and wheel.

## Privacy

> **Fitness data is special-category personal data under GDPR Art. 9.**
> This repository is designed for **single-user, self-hosted deployment**.
> Do not run it as a multi-tenant service. Logs at `INFO` and above never
> include GPS coordinates, FIT user-field strings, user names, or email
> addresses; `DEBUG` may include more and **must not** be enabled in
> production. Token files live under `MCP_TOKEN_DIR` with mode `0600`.
> Test fixtures use synthetic FITs and PII-scrubbed API recordings — real
> exports never enter the repo.

See [docs/architecture.md](docs/architecture.md) for the privacy boundary
in full and [CLAUDE.md](CLAUDE.md) for the engineering conventions that
enforce it.

## Status

Phase 0 — scaffolding. Both servers boot and respond to `/health`. No
provider integrations yet. See [docs/roadmap.md](docs/roadmap.md) for the
phased plan.

## Development

```bash
# One-time: install uv (https://docs.astral.sh/uv/)
pipx install uv

# Create a dev venv with the workspace dev tools
uv venv
source .venv/bin/activate
uv pip install -e ./packages/mcp-fitness-shared \
               -e ./packages/mcp-stryd \
               -e ./packages/mcp-garmin \
               ruff mypy pytest pytest-asyncio respx httpx

# Lint, type-check, test
ruff check .
mypy --strict packages/mcp-fitness-shared/src packages/mcp-stryd/src packages/mcp-garmin/src
pytest packages/mcp-fitness-shared packages/mcp-stryd packages/mcp-garmin
```

## License

[GPL-3.0](LICENSE) © Eduard Ralph

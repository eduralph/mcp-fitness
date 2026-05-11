# mcp-garmin

[MCP](https://modelcontextprotocol.io/) server exposing
[Garmin](https://www.garmin.com/) activity data to
[claude.ai](https://claude.ai/) via HTTP/SSE. Part of the
[mcp-fitness](https://github.com/eduralph/mcp-fitness) monorepo.

The **FIT-file watcher** is the primary, robust integration (Phase 2).
**Garmin Connect** scraping via the community `garminconnect` library is
opt-in and best-effort (Phase 3) — it works when it works, and when it
doesn't the server returns clean structured errors instead of crashing.

## Status

**Phase 0 — server boots, `/health` works.** No FIT or Connect code
yet. See [../../docs/roadmap.md](../../docs/roadmap.md) for the phased
plan.

## Install

```bash
pip install mcp-garmin
```

Or via Docker (GHCR releases land in Phase 2):

```bash
docker pull ghcr.io/eduralph/mcp-garmin:latest
```

## Run

```bash
export MCP_HOST=0.0.0.0
export MCP_PORT=8080
export MCP_LOG_LEVEL=INFO
export MCP_TOKEN_DIR=/data/tokens   # mode 0600 enforced
python -m mcp_garmin
# → HTTP transport on http://0.0.0.0:8080, /health returns 200
```

## Configuration

Phase 0 reads only the shared `MCP_*` variables. Phase 2 will add:

| Variable | Purpose |
|---|---|
| `MCP_GARMIN_FIT_DIR` | Bind-mounted directory the FIT auto-export pipeline writes into (read-only) |

Phase 3, opt-in:

| Variable | Purpose |
|---|---|
| `MCP_GARMIN_CONNECT_ENABLED` | `true` to enable the Connect tools |
| `MCP_GARMIN_CONNECT_EMAIL` | Garmin Connect account |
| `MCP_GARMIN_CONNECT_PASSWORD` | Garmin Connect password |

## Privacy

> Garmin data includes GPS tracks, heart rate, and other physiological
> measurements. This is **special-category personal data under GDPR
> Art. 9**. Run this only for yourself. Logs at `INFO` and above never
> include GPS coordinates, user names, emails, or FIT user-field
> strings; `DEBUG` may include more — do not enable in production.

## Garmin Connect — best-effort warning

> The Connect path depends on the unofficial
> [`garminconnect`](https://github.com/cyberjunky/python-garminconnect)
> library, which scrapes endpoints Garmin can change without notice.
> When Connect breaks, `connect_*` tools return structured
> `{"error": "connect_unavailable", ...}` responses; the FIT path keeps
> working. **Use the FIT path as your primary integration.**

## Develop

```bash
uv pip install -e . -e ../mcp-fitness-shared "fastmcp" "pytest" "pytest-asyncio" "respx" "httpx"
ruff check .
mypy --strict src
pytest
```

## License

[GPL-3.0](../../LICENSE) © Eduard Ralph

# mcp-fitness — Architecture

## Design principles

- **Two servers, one repo.** Each MCP has its own package, its own
  pyproject.toml, its own Dockerfile, its own CI matrix. They version
  independently and deploy independently.
- **Shared utilities, not shared business logic.** A `mcp-fitness-shared`
  package holds config patterns, logging, token storage, health endpoint.
  It does **not** know about Stryd or Garmin specifics.
- **Async everywhere.** Provider API calls are I/O-bound. FastMCP supports
  async tool handlers; use them.
- **Configuration via env vars.** Compose-friendly, secret-friendly. No
  magic file paths.
- **Graceful degradation.** mcp-garmin running without FIT directory
  configured returns clear "not configured" errors per-tool, not startup
  failures.
- **No personal data in logs at INFO+.** DEBUG may include more for
  local development; production runs at INFO.

## Deployment topology

```
              ┌──────────────────────────────┐
              │      claude.ai (browser)     │
              └──────┬───────────────┬───────┘
                     │               │
                     │ MCP/HTTP+SSE  │
                     ▼               ▼
       ┌────────────────────┐  ┌────────────────────┐
       │  Cloudflare edge   │  │  Cloudflare edge   │
       │  Access (Google)   │  │  Access (Google)   │
       └─────────┬──────────┘  └─────────┬──────────┘
                 │ Tunnel                │ Tunnel
                 ▼                       ▼
       ┌────────────────────┐  ┌────────────────────┐
       │     mcp-stryd      │  │     mcp-garmin     │
       │     container      │  │     container      │
       │  (port 8080)       │  │  (port 8080)       │
       └─────────┬──────────┘  └─────────┬──────────┘
                 │                       │
                 ▼                       ▼
            Stryd API           Local FIT folder
            (HTTPS)             (bind-mount, ro)
                                +
                                garminconnect lib
                                (Phase 3, fragile)
```

Both containers run on the `cloudflared_proxy` Docker network. The same
cloudflared instance routes both hostnames.

## Monorepo layout

```
mcp-fitness/
├── .github/
│   └── workflows/
│       ├── ci.yml                      # tests both packages on push/PR
│       ├── release-stryd.yml           # tag mcp-stryd-vX.Y.Z → PyPI + GHCR
│       └── release-garmin.yml          # tag mcp-garmin-vX.Y.Z → PyPI + GHCR
├── packages/
│   ├── mcp-fitness-shared/
│   │   ├── pyproject.toml
│   │   ├── src/mcp_fitness_shared/
│   │   │   ├── __init__.py
│   │   │   ├── config.py               # pydantic-settings base
│   │   │   ├── logging.py              # structured JSON, PII redaction
│   │   │   ├── tokens.py               # atomic file r/w, mode 0600
│   │   │   └── health.py               # /health endpoint factory
│   │   └── tests/
│   ├── mcp-stryd/
│   │   ├── pyproject.toml              # depends on mcp-fitness-shared
│   │   ├── Dockerfile
│   │   ├── docker-compose.example.yml
│   │   ├── src/mcp_stryd/
│   │   │   ├── __init__.py
│   │   │   ├── __main__.py             # python -m mcp_stryd
│   │   │   ├── server.py               # FastMCP instance + tool registration
│   │   │   ├── config.py               # Stryd-specific settings
│   │   │   ├── client.py               # async httpx client + OAuth
│   │   │   ├── auth.py                 # OAuth2 authorization code flow
│   │   │   ├── models.py               # pydantic data models
│   │   │   └── tools.py                # @mcp.tool definitions
│   │   ├── tests/
│   │   │   ├── conftest.py
│   │   │   ├── fixtures/
│   │   │   │   ├── stryd_activity.json
│   │   │   │   ├── stryd_token.json
│   │   │   │   └── stryd_cp_history.json
│   │   │   ├── test_client.py
│   │   │   ├── test_auth.py
│   │   │   └── test_tools.py
│   │   └── README.md
│   └── mcp-garmin/
│       ├── pyproject.toml              # depends on mcp-fitness-shared
│       ├── Dockerfile
│       ├── docker-compose.example.yml
│       ├── src/mcp_garmin/
│       │   ├── __init__.py
│       │   ├── __main__.py
│       │   ├── server.py
│       │   ├── config.py
│       │   ├── fit/
│       │   │   ├── __init__.py
│       │   │   ├── watcher.py          # watchdog-based folder watcher
│       │   │   ├── parser.py           # fitparse wrapper
│       │   │   └── models.py
│       │   ├── connect/
│       │   │   ├── __init__.py
│       │   │   ├── client.py           # garminconnect wrapper
│       │   │   └── health.py           # background health-check task
│       │   └── tools.py
│       ├── tests/
│       │   ├── conftest.py
│       │   ├── fixtures/
│       │   │   ├── synthetic.fit
│       │   │   └── connect_activity.json
│       │   ├── test_fit_parser.py
│       │   ├── test_fit_watcher.py
│       │   ├── test_connect_client.py
│       │   └── test_tools.py
│       └── README.md
├── docs/
│   ├── deployment.md                   # Synology + Cloudflare Tunnel walkthrough
│   ├── stryd-setup.md                  # OAuth registration + first auth
│   ├── garmin-fit-setup.md             # FIT auto-export pipeline
│   ├── garmin-connect-setup.md         # Phase 3, fragile path
│   └── claude-setup.md                 # adding both MCPs in claude.ai
├── docker-compose.example.yml          # repo-level example with both services
├── pyproject.toml                      # workspace-level dev tools (ruff, mypy)
├── ruff.toml
├── mypy.ini
├── README.md                           # repo-level intro and links
├── LICENSE                             # GPL-3.0
├── CHANGELOG.md                        # per-package changelogs linked
└── CLAUDE.md                           # conventions for Claude Code sessions
```

## Package dependencies

```
mcp-stryd ───┐
             ├──▶ mcp-fitness-shared
mcp-garmin ──┘
```

`mcp-fitness-shared` is **internal-only** — not published to PyPI. Each
of the public packages declares it as a path dependency in its
`pyproject.toml` and pulls it into its Docker image via a build context
that includes both directories. The user installs `mcp-stryd` or
`mcp-garmin` from PyPI without ever knowing the shared layer exists.

## Per-package configuration

Each package has its own env-var namespace. Both share a few common
settings inherited from `mcp-fitness-shared`.

### Shared (both)

```bash
MCP_HOST=0.0.0.0
MCP_PORT=8080
MCP_LOG_LEVEL=INFO
MCP_TOKEN_DIR=/data/tokens
```

### mcp-stryd only

```bash
MCP_STRYD_CLIENT_ID=…
MCP_STRYD_CLIENT_SECRET=…
MCP_STRYD_REDIRECT_URI=https://mcp-stryd.ralphovi.net/oauth/callback
```

### mcp-garmin only

```bash
# FIT-file source (Phase 2)
MCP_GARMIN_FIT_DIR=/data/fit

# Connect source (Phase 3, opt-in)
MCP_GARMIN_CONNECT_ENABLED=false
MCP_GARMIN_CONNECT_EMAIL=…
MCP_GARMIN_CONNECT_PASSWORD=…
```

## Tool inventories

claude.ai shows tools namespaced by server name automatically. Tool names
within each server don't need a prefix.

### mcp-stryd tools

| Tool | Returns |
|---|---|
| `list_activities(start_date, end_date, limit)` | Activity summaries |
| `get_activity(activity_id)` | Activity with power curve, zones, RSS, form metrics |
| `get_cp_history(weeks)` | Time series of CP measurements |
| `get_training_balance(date)` | CTL, ATL, TSB on that date |
| `get_zones()` | Current power zone definitions |

### mcp-garmin tools (FIT source — Phase 2)

| Tool | Returns |
|---|---|
| `list_fit_files(start_date, end_date)` | Filenames + timestamps in watched folder |
| `parse_fit(filename)` | Full activity record incl. laps, samples |

### mcp-garmin tools (Connect source — Phase 3, flag-gated)

| Tool | Returns |
|---|---|
| `connect_list_activities(start_date, end_date, limit)` | Activity summaries |
| `connect_get_activity(activity_id)` | Activity record from Connect |
| `connect_health()` | Status of the unofficial library, last successful call |

When `MCP_GARMIN_CONNECT_ENABLED=false`, the connect_* tools are still
registered but each call returns a structured error
`{"error": "connect_disabled"}` — never crashes the process.

## Cross-MCP composition (deferred)

Things like "weekly digest" or "compare what Stryd and Garmin recorded
for yesterday's run" require data from both servers. Three options for
where this lives:

1. **In Claude itself.** The model calls both MCPs and synthesizes.
   This is the default — no extra infrastructure.
2. **A third server (`mcp-fitness-composite`).** Calls both via their
   HTTP endpoints. Cleanest separation but introduces MCP-to-MCP
   plumbing.
3. **A composite layer in one of the existing servers.** Pragmatic but
   muddies the boundary.

**Decision: defer until Phase 4.** Use option 1 (Claude composes) until
we hit concrete pain. The Project Instructions in the Running Project
can teach Claude the composition patterns; no code change required.

## OAuth flow (mcp-stryd only)

1. Boot mcp-stryd configured with client ID/secret.
2. Open `https://mcp-stryd.ralphovi.net/oauth/start` in a browser.
3. Cloudflare Access authenticates → me.
4. Server redirects to Stryd's authorize URL.
5. Stryd redirects back to `/oauth/callback?code=…`.
6. Server exchanges the code for access + refresh tokens, writes to
   `/data/tokens/stryd.json` with mode 0600.
7. Subsequent tool calls refresh on 401 automatically.

If the refresh token expires, tools log a structured `auth_required`
error and continue erroring until step 2 is repeated.

## FIT file ingestion (mcp-garmin Phase 2)

The watched folder is a bind-mount; the auto-export pipeline on the
workstation drops FIT files there. The MCP doesn't care how they arrive,
only that they appear.

On startup, mcp-garmin scans the folder once and builds an in-memory
index keyed by `(filename, hash)`. `watchdog` then handles incremental
changes. Parsed activity records cache to disk in
`/data/tokens/garmin-fit-cache/<hash>.json` so repeated tool calls
during one conversation don't re-parse.

Log line on indexing a new file: `indexed activity {timestamp} from
{filename}` — no GPS, no user-field strings.

## Garmin Connect (Phase 3) — fragile by design

`garminconnect` is the community-maintained scraping library. It works
when it works. The integration:

- **Off by default** (`MCP_GARMIN_CONNECT_ENABLED=false`).
- Isolated in `src/mcp_garmin/connect/`. The FIT path doesn't import it
  and doesn't depend on it.
- A background task pings Connect every 30 minutes and exposes the
  result via the `connect_health` tool.
- Each tool call wraps the library in try/except. Auth failures, network
  failures, and parsing failures are distinct structured errors.
- The version of `garminconnect` in use is logged at startup so when it
  breaks I know which version to check.

The README must say **loudly** that this is best-effort. The FIT path
is the primary, robust integration.

## Logging and observability

Structured JSON to stdout (Docker captures, DSM forwards). PII redaction
is enforced in the `mcp-fitness-shared` logging module — fields known to
contain PII (gps_lat, gps_lon, user_name, user_email, fit_user_field)
are stripped before serialization.

Per-server health endpoint at `/health` returns:

- `200` with `{"status": "ok", "providers": {…}}` if process is up and
  all configured providers are reachable
- `503` if a configured provider has been failing for >5 minutes

## CI/CD

- **Push/PR:** `ci.yml` runs ruff + mypy + pytest on both packages
  independently. Matrix: Python 3.12, 3.13.
- **Tag `mcp-stryd-v*`:** `release-stryd.yml` builds the wheel, publishes
  to PyPI, builds the Docker image, publishes to
  `ghcr.io/eduralph/mcp-stryd:vX.Y.Z` and `:latest`.
- **Tag `mcp-garmin-v*`:** same, for `mcp-garmin`.
- `mcp-fitness-shared` never publishes to PyPI; it ships inside each
  Docker image via the build context.

## Synology Compose example (repo-level)

```yaml
services:
  mcp-stryd:
    image: ghcr.io/eduralph/mcp-stryd:latest
    container_name: mcp-stryd
    restart: unless-stopped
    env_file: ./mcp-stryd.env
    volumes:
      - ./tokens/stryd:/data/tokens
    networks: [cloudflared_proxy]
    healthcheck:
      test: ["CMD", "curl", "-fsS", "http://localhost:8080/health"]
      interval: 60s

  mcp-garmin:
    image: ghcr.io/eduralph/mcp-garmin:latest
    container_name: mcp-garmin
    restart: unless-stopped
    env_file: ./mcp-garmin.env
    volumes:
      - ./tokens/garmin:/data/tokens
      - /volume1/garmin-fit:/data/fit:ro
    networks: [cloudflared_proxy]
    healthcheck:
      test: ["CMD", "curl", "-fsS", "http://localhost:8080/health"]
      interval: 60s

networks:
  cloudflared_proxy:
    external: true
```

Two `.env` files (also gitignored), one per service.

Cloudflare Tunnel ingress (Zero Trust dashboard):

| Hostname | Service URL | Access policy |
|---|---|---|
| `mcp-stryd.ralphovi.net` | `http://mcp-stryd:8080` | Google Workspace, me only |
| `mcp-garmin.ralphovi.net` | `http://mcp-garmin:8080` | Google Workspace, me only |

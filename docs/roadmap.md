# mcp-fitness — Roadmap

Phased plan. Each phase is a shippable milestone.

## Phase 0 — Repo scaffolding

**Goal:** the monorepo exists, both packages have skeletons, CI runs,
both servers respond to `/health`.

- [ ] Create `eduralph/mcp-fitness` on GitHub, GPL-3.0, no branch protection
- [ ] Initial commit: top-level README, LICENSE, .gitignore, workspace
      `pyproject.toml`, ruff.toml, mypy.ini, CLAUDE.md
- [ ] `packages/mcp-fitness-shared/` with `config.py`, `logging.py`,
      `tokens.py`, `health.py` — bare minimum implementations
- [ ] `packages/mcp-stryd/` with FastMCP instantiation, single `health()`
      tool, Dockerfile, package README
- [ ] `packages/mcp-garmin/` with the same skeleton
- [ ] `python -m mcp_stryd` and `python -m mcp_garmin` both boot and
      respond
- [ ] `tests/test_server.py` in each package smoke-tests the health tool
- [ ] GitHub Actions: ruff + mypy + pytest for both packages, matrix
      Python 3.12 + 3.13
- [ ] Both Dockerfiles build, produce working images
- [ ] Repo-level `docker-compose.example.yml` with both services
- [ ] Per-package `CHANGELOG.md` files with `0.1.0 — initial scaffold`

**Exit criterion:** `docker compose up` brings both containers up, both
`/health` endpoints return 200.

## Phase 1 — mcp-stryd

**Goal:** Claude in the Running Project can answer "summarize my last
week of running from Stryd" without me pasting anything.

### Prerequisites

- [ ] Verify Stryd API access is included with my subscription
- [ ] Register a developer application in the Stryd portal; capture
      client ID + secret outside the repo

### Implementation

- [ ] `packages/mcp-stryd/src/mcp_stryd/auth.py` — OAuth2 authorization
      code flow, callback endpoint, atomic token persistence
- [ ] `client.py` — `httpx.AsyncClient` with retry on transient errors
      and automatic refresh on 401
- [ ] `models.py` — pydantic models for activity, power curve, zones,
      training balance responses
- [ ] Tools:
  - `list_activities(start_date, end_date, limit)`
  - `get_activity(activity_id)`
  - `get_cp_history(weeks)`
  - `get_training_balance(date)`
  - `get_zones()`
- [ ] Tests with `respx` mocking Stryd API response shapes (fixtures
      scrubbed of PII)
- [ ] `docs/stryd-setup.md` — "I have a Stryd account" to "tokens stored,
      server running"
- [ ] Deploy to Synology: `/volume1/docker/mcp-stryd/`, wire Cloudflare
      Tunnel + Access, connect from claude.ai, validate end-to-end
- [ ] Tag `mcp-stryd-v0.2.0`, GitHub Actions publishes to PyPI + GHCR

**Exit criterion:** In the Running Project, "summarize my last week of
running from Stryd" works end-to-end.

## Phase 2 — mcp-garmin via FIT files

**Goal:** when a FIT file lands in the watched folder via my automated
export pipeline, the MCP indexes it and Claude can analyze it.

### Prerequisites

- [ ] Garmin auto-export pipeline producing FIT files in a directory the
      Synology can mount (you confirmed you can automate this)
- [ ] Bind-mount strategy decided: SMB share, NFS, rsync target, …

### Implementation

- [ ] `packages/mcp-garmin/src/mcp_garmin/fit/parser.py` — `fitparse`
      wrapper, output normalized to `models.ActivityRecord`
- [ ] `fit/watcher.py` — `watchdog`-based watcher, in-memory index keyed
      by `(filename, hash)`
- [ ] Disk cache for parsed activities at `/data/tokens/garmin-fit-cache/`
      (parsing is fast but repeated tool calls in one conversation
      shouldn't re-parse)
- [ ] Tools:
  - `list_fit_files(start_date, end_date)`
  - `parse_fit(filename)`
- [ ] Tests with synthetic FITs: outdoor run + GPS, indoor treadmill,
      structured workout with laps, multi-sport (skipped explicitly)
- [ ] `docs/garmin-fit-setup.md` — auto-export pipeline + bind-mount
      configuration
- [ ] Update `docs/deployment.md` and the repo-level compose example
      with the FIT volume mount
- [ ] Tag `mcp-garmin-v0.2.0`, publish to PyPI + GHCR

**Exit criterion:** In the Running Project, "analyze yesterday's run
using the FIT file" works without pasting the file.

## Phase 3 — mcp-garmin Connect (best-effort, opt-in)

**Goal:** when Garmin Connect's unofficial API is working, mcp-garmin
can use it. When it's broken, tools return clean errors and the FIT
path keeps working.

### Implementation

- [ ] `packages/mcp-garmin/src/mcp_garmin/connect/client.py` — thin
      wrapper around `garminconnect`, isolated from FIT code
- [ ] Email/password env vars, token cached after first success,
      automatic refresh on auth failure
- [ ] Background health detector pings Connect every 30 minutes,
      updates a status flag in memory
- [ ] Tools (gated on `MCP_GARMIN_CONNECT_ENABLED`):
  - `connect_list_activities(start_date, end_date, limit)`
  - `connect_get_activity(activity_id)`
  - `connect_health()`
- [ ] When the library breaks, tools return
      `{"error": "connect_unavailable", "since": "..."}` — never crash
- [ ] README states **loudly** that this is best-effort and dependent
      on the unofficial library
- [ ] `docs/garmin-connect-setup.md` with manual recovery flow

**Exit criterion:** when Connect is working, queries succeed silently.
When it breaks, failure mode is clean, log messages are clear, and the
FIT path is unaffected.

## Phase 4 — Composite analysis

**Goal:** higher-order questions ("how is my fitness trending compared
to four weeks ago," "race in 14 days, what's my form") are answered
fluidly.

The decision in **mcp-02-architecture** is: **Claude composes**. The
Project Instructions in the Running Project teach Claude the patterns;
no new server, no new tools.

### Implementation

- [ ] In the Running Project, add a knowledge file
      `run-04-mcp-query-patterns.md` documenting:
  - How to ask Claude for a weekly digest using both MCPs
  - How to ask for a cycle summary across N weeks
  - How to ask for race readiness given an upcoming date
- [ ] Tune Project Instructions in the Running Project to reference
      mcp-stryd and mcp-garmin tools by name where helpful
- [ ] Iterate on the patterns based on real use; if a composite is
      asked for repeatedly, reconsider whether it deserves a dedicated
      MCP tool

**Exit criterion:** Monday-morning "what's my week look like" returns
a useful answer in one Claude turn.

## Phase 5 — Polish for public release

**Goal:** a stranger with the same hardware deploys this in an evening.

- [ ] Comprehensive `docs/deployment.md` covering Synology, Linux
      Docker, and bare metal Python install
- [ ] Each package's README covers install, configure, and one example
      Claude conversation
- [ ] PyPI: `pip install mcp-stryd` and `pip install mcp-garmin` both
      work
- [ ] GHCR Docker images for both packages
- [ ] Tagged releases on GitHub with semver
- [ ] Repo-level README has a "who this is for / who it isn't" section
      and links to both packages
- [ ] Announce when there's something worth announcing

**Exit criterion:** a stranger files a useful issue or sends a useful PR.

## Out of scope

- Writing data back to Stryd or Garmin
- Real-time data during a workout
- Other providers (Strava, TrainingPeaks, Polar, COROS) — architecture
  supports them; adding any is a separate package, separate decision
- Web UI
- Multi-tenancy

## Known risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Stryd API auth or schema changes break Phase 1 | Low | High | Pin API version in headers; alert on 4xx spikes. Stryd is partner-facing so changes are usually announced. |
| Garmin Connect scraping breaks (Phase 3) | High | Medium | Already designed as best-effort. FIT path is the primary integration and survives Garmin's auth wars indefinitely. |
| FastMCP API churn before 1.0 | Medium | Low | The official `mcp` Python SDK is more stable; drop down a layer if needed. |
| Stryd reduces API access | Low | High | Verify current API access is included with the regular Stryd subscription as a Phase 1 prerequisite. |
| FIT auto-export pipeline fragile | Medium | Medium | You confirmed you can automate this. If the upstream sync ever breaks, manual FIT export is the fallback — same code path. |
| Two containers double the deployment burden | Low | Low | Same `cloudflared_proxy` network, same compose patterns, same Synology Task Scheduler. Marginal additional overhead. |

## Current state

- **Phase:** 0 (not yet started)
- **Next action:** create `eduralph/mcp-fitness` on GitHub, push initial scaffold
- **Blocker for Phase 1:** verify Stryd API access; register developer app
- **Blocker for Phase 2:** confirm FIT auto-export pipeline lands files in
  a Synology-accessible directory
- **Last updated:** TODO date

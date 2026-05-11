# mcp-stryd

[MCP](https://modelcontextprotocol.io/) server exposing
[Stryd](https://www.stryd.com/) power-based training data to
[claude.ai](https://claude.ai/) via HTTP/SSE. Part of the
[mcp-fitness](https://github.com/eduralph/mcp-fitness) monorepo.

## Status

**Phase 0 — server boots, `/health` works.** No Stryd API calls yet;
Phase 1 will add OAuth2, the async HTTP client, and the activity /
power-curve / CP-history / training-balance / zones tools. See
[../../docs/roadmap.md](../../docs/roadmap.md).

## Install

```bash
pip install mcp-stryd
```

Or via Docker (GHCR releases land in Phase 1):

```bash
docker pull ghcr.io/eduralph/mcp-stryd:latest
```

## Run

```bash
export MCP_HOST=0.0.0.0
export MCP_PORT=8080
export MCP_LOG_LEVEL=INFO
export MCP_TOKEN_DIR=/data/tokens   # mode 0600 enforced
python -m mcp_stryd
# → HTTP transport on http://0.0.0.0:8080, /health returns 200
```

## Configuration

Phase 0 reads only the shared `MCP_*` variables. Phase 1 will add:

| Variable | Purpose |
|---|---|
| `MCP_STRYD_CLIENT_ID` | OAuth2 client ID issued by Stryd |
| `MCP_STRYD_CLIENT_SECRET` | OAuth2 client secret |
| `MCP_STRYD_REDIRECT_URI` | Full callback URL exposed via Cloudflare Tunnel |

## Privacy

> Stryd data describes your training and physiology. It is
> **special-category personal data under GDPR Art. 9**. Run this only
> for yourself. Logs at `INFO` and above never include GPS, user names,
> emails, or FIT user-fields; `DEBUG` may include more — do not enable
> in production. Tokens live under `MCP_TOKEN_DIR` with mode `0600`.

## Develop

```bash
uv pip install -e . -e ../mcp-fitness-shared "fastmcp" "pytest" "pytest-asyncio" "respx" "httpx"
ruff check .
mypy --strict src
pytest
```

## License

[GPL-3.0](../../LICENSE) © Eduard Ralph

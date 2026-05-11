# mcp-garmin Docker image.
#
# Build context: the repository root, so the path-dependency on
# mcp-fitness-shared resolves. The repo-level
# docker-compose.example.yml does this; for a standalone build:
#
#   docker build -f packages/mcp-garmin/Dockerfile -t mcp-garmin:dev .
#
# (Run from the repo root, not from inside packages/mcp-garmin/.)

FROM python:3.13-slim AS builder

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /build

COPY packages/mcp-fitness-shared /build/mcp-fitness-shared
COPY packages/mcp-garmin /build/mcp-garmin

RUN pip install --upgrade pip \
 && pip install /build/mcp-fitness-shared \
 && pip install /build/mcp-garmin

# ---- runtime image ----
FROM python:3.13-slim AS runtime

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    MCP_HOST=0.0.0.0 \
    MCP_PORT=8080 \
    MCP_LOG_LEVEL=INFO \
    MCP_TOKEN_DIR=/data/tokens

RUN groupadd --system --gid 10001 app \
 && useradd --system --uid 10001 --gid app --home-dir /home/app --create-home app \
 && mkdir -p /data/tokens /data/fit \
 && chown -R app:app /data

COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

USER app
WORKDIR /home/app

EXPOSE 8080

HEALTHCHECK --interval=60s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://localhost:8080/health', timeout=3).status==200 else 1)"

ENTRYPOINT ["python", "-m", "mcp_garmin"]

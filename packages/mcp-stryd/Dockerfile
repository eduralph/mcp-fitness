# mcp-stryd Docker image.
#
# Build context: the repository root, so the path-dependency on
# mcp-fitness-shared resolves. The repo-level
# docker-compose.example.yml does this; for a standalone build:
#
#   docker build -f packages/mcp-stryd/Dockerfile -t mcp-stryd:dev .
#
# (Run from the repo root, not from inside packages/mcp-stryd/.)

FROM python:3.13-slim AS builder

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /build

# Install both packages — order matters: shared first so the path
# dependency resolves when mcp-stryd is installed.
COPY packages/mcp-fitness-shared /build/mcp-fitness-shared
COPY packages/mcp-stryd /build/mcp-stryd

RUN pip install --upgrade pip \
 && pip install /build/mcp-fitness-shared \
 && pip install /build/mcp-stryd

# ---- runtime image ----
FROM python:3.13-slim AS runtime

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    MCP_HOST=0.0.0.0 \
    MCP_PORT=8080 \
    MCP_LOG_LEVEL=INFO \
    MCP_TOKEN_DIR=/data/tokens

# Non-root user owns the data volume.
RUN groupadd --system --gid 10001 app \
 && useradd --system --uid 10001 --gid app --home-dir /home/app --create-home app \
 && mkdir -p /data/tokens \
 && chown -R app:app /data

# Copy the installed site-packages from the builder.
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

USER app
WORKDIR /home/app

EXPOSE 8080

HEALTHCHECK --interval=60s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://localhost:8080/health', timeout=3).status==200 else 1)"

ENTRYPOINT ["python", "-m", "mcp_stryd"]

# Changelog

Each published package keeps its own changelog. The monorepo doesn't
ship as a single artifact, so there's no unified version here.

- **mcp-stryd** → [packages/mcp-stryd/CHANGELOG.md](packages/mcp-stryd/CHANGELOG.md)
- **mcp-garmin** → [packages/mcp-garmin/CHANGELOG.md](packages/mcp-garmin/CHANGELOG.md)
- **mcp-fitness-shared** is internal-only and is not versioned for
  release. Its source ships inside each public package's Docker image
  and wheel.

Releases are tagged on GitHub with a per-package prefix —
`mcp-stryd-vX.Y.Z` and `mcp-garmin-vX.Y.Z` — and trigger matching
GitHub Actions workflows that publish to PyPI and GHCR.

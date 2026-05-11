"""Atomic JSON token storage.

Tokens (Stryd OAuth refresh tokens, future Garmin Connect session
cookies, …) live as small JSON files under ``MCP_TOKEN_DIR``. Two
invariants:

1. **Atomic.** A reader must never observe a half-written file. We
   write to a temp file in the same directory, ``fsync`` it, then
   ``os.replace`` — a POSIX-atomic rename on the same filesystem.

2. **Mode 0600.** Only the container's process user reads or writes
   them. We chmod the temp file before the rename so the final inode
   is created with the restricted mode.
"""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any


def read_token_file(path: Path) -> dict[str, Any] | None:
    """Return the parsed JSON contents, or ``None`` if the file does not exist.

    Raises whatever :func:`json.loads` raises if the file is present
    but malformed — callers should treat that as a configuration error,
    not a recoverable runtime condition.
    """
    if not path.exists():
        return None
    raw = path.read_text(encoding="utf-8")
    parsed: Any = json.loads(raw)
    if not isinstance(parsed, dict):
        msg = f"token file {path} did not contain a JSON object"
        raise TypeError(msg)
    return parsed


def write_token_file(path: Path, data: dict[str, Any]) -> None:
    """Atomically write ``data`` as JSON to ``path`` with mode 0600.

    Creates parent directories if they don't exist. The temp file is
    cleaned up on error so a half-written rename never lingers.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(
        dir=path.parent,
        prefix=f".{path.name}.",
        suffix=".tmp",
    )
    tmp_path = Path(tmp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, sort_keys=True, separators=(",", ":"))
            f.flush()
            os.fsync(f.fileno())
        tmp_path.chmod(0o600)
        tmp_path.replace(path)
    except BaseException:
        tmp_path.unlink(missing_ok=True)
        raise

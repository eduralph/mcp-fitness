"""Tests for mcp_fitness_shared.tokens."""

from __future__ import annotations

import json
import stat
from typing import TYPE_CHECKING

import pytest

from mcp_fitness_shared.tokens import read_token_file, write_token_file

if TYPE_CHECKING:
    from pathlib import Path


def test_read_returns_none_when_missing(tmp_path: Path) -> None:
    assert read_token_file(tmp_path / "nope.json") is None


def test_roundtrip(tmp_path: Path) -> None:
    path = tmp_path / "tok.json"
    data = {"access_token": "a", "refresh_token": "b", "expires_at": 1700000000}
    write_token_file(path, data)
    assert read_token_file(path) == data


def test_writes_mode_0600(tmp_path: Path) -> None:
    path = tmp_path / "tok.json"
    write_token_file(path, {"k": "v"})
    mode = stat.S_IMODE(path.stat().st_mode)
    assert mode == 0o600


def test_creates_parent_dirs(tmp_path: Path) -> None:
    path = tmp_path / "nested" / "deeper" / "tok.json"
    write_token_file(path, {"k": "v"})
    assert path.exists()


def test_atomic_no_tmp_left_behind_on_success(tmp_path: Path) -> None:
    path = tmp_path / "tok.json"
    write_token_file(path, {"k": "v"})
    leftovers = [p for p in tmp_path.iterdir() if p.name.endswith(".tmp")]
    assert leftovers == []


def test_overwrite_preserves_atomicity(tmp_path: Path) -> None:
    path = tmp_path / "tok.json"
    write_token_file(path, {"version": 1})
    write_token_file(path, {"version": 2})
    assert read_token_file(path) == {"version": 2}
    mode = stat.S_IMODE(path.stat().st_mode)
    assert mode == 0o600


def test_read_rejects_non_object(tmp_path: Path) -> None:
    path = tmp_path / "tok.json"
    path.write_text(json.dumps([1, 2, 3]))
    with pytest.raises(TypeError, match="did not contain a JSON object"):
        read_token_file(path)


def test_cleans_up_tmp_on_serialization_error(tmp_path: Path) -> None:
    path = tmp_path / "tok.json"

    class NotJSONSerializable:
        pass

    with pytest.raises(TypeError):
        write_token_file(path, {"bad": NotJSONSerializable()})  # type: ignore[dict-item]
    leftovers = [p for p in tmp_path.iterdir() if p.name.endswith(".tmp")]
    assert leftovers == []
    assert not path.exists()

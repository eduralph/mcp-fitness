"""Tests for mcp_fitness_shared.logging — processor unit tests + the
fully-configured integration path that is the actual privacy contract."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

from mcp_fitness_shared.logging import (
    PII_KEYS,
    REDACTED,
    configure_logging,
    get_logger,
    redact_pii,
)

if TYPE_CHECKING:
    import pytest

# --- redact_pii processor (unit) --------------------------------------


def test_redacts_known_keys_at_info() -> None:
    event = {
        "event": "indexed",
        "gps_lat": 47.123,
        "gps_lon": 8.456,
        "user_name": "Eduard",
        "user_email": "eduard@example.com",
        "fit_user_field": "secret-token",
        "power": 250,
    }
    out = redact_pii(None, "info", event)
    for key in PII_KEYS:
        assert out[key] == REDACTED
    assert out["power"] == 250
    assert out["event"] == "indexed"


def test_does_not_redact_at_debug() -> None:
    event = {"event": "indexed", "gps_lat": 47.123, "user_email": "x@y"}
    out = redact_pii(None, "debug", event)
    assert out["gps_lat"] == 47.123
    assert out["user_email"] == "x@y"


def test_redacts_at_warning_and_error() -> None:
    for method in ("warning", "error", "critical"):
        event = {"gps_lon": 8.456}
        out = redact_pii(None, method, event)
        assert out["gps_lon"] == REDACTED


def test_unknown_method_treated_as_info() -> None:
    event = {"user_email": "x@y"}
    out = redact_pii(None, "nonsense", event)
    assert out["user_email"] == REDACTED


def test_no_op_when_no_pii_present() -> None:
    event = {"event": "ok", "power": 200, "duration_s": 3600}
    out = redact_pii(None, "info", dict(event))
    assert out == event


# --- configure_logging integration ------------------------------------
#
# These are the tests that actually back CLAUDE.md's claim that "PII
# redaction is enforced in the shared logging module." The unit tests
# above check the processor in isolation; these verify it's wired into
# the chain so the bound logger that real code uses produces redacted
# JSON.


def _last_json_line(out: str) -> dict[str, object]:
    """Take the last non-empty stdout line and parse it as JSON."""
    lines = [line for line in out.splitlines() if line.strip()]
    assert lines, f"no JSON log lines captured. raw output: {out!r}"
    return json.loads(lines[-1])  # type: ignore[no-any-return]


def test_configure_at_info_emits_json_with_pii_redacted(
    capsys: pytest.CaptureFixture[str],
) -> None:
    configure_logging(level="INFO")
    log = get_logger("test.module")
    log.info(
        "indexed_activity",
        power=250,
        duration_s=3600,
        gps_lat=47.123,
        gps_lon=8.456,
        user_email="eduard@example.com",
        user_name="Eduard",
        fit_user_field="secret-token",
    )
    payload = _last_json_line(capsys.readouterr().out)

    # Non-PII fields preserved.
    assert payload["event"] == "indexed_activity"
    assert payload["power"] == 250
    assert payload["duration_s"] == 3600
    assert payload["level"] == "info"
    assert "timestamp" in payload

    # Every known PII field redacted — not absent (we want monitoring
    # to see that something was scrubbed), but never the original value.
    for key in PII_KEYS:
        assert payload[key] == REDACTED, f"{key} leaked at INFO"


def test_configure_at_warning_still_redacts(
    capsys: pytest.CaptureFixture[str],
) -> None:
    configure_logging(level="WARNING")
    log = get_logger()
    log.warning("upstream_5xx", gps_lat=47.123, status_code=503)
    payload = _last_json_line(capsys.readouterr().out)
    assert payload["gps_lat"] == REDACTED
    assert payload["status_code"] == 503


def test_configure_at_debug_passes_pii_through(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """DEBUG is developer-only; CLAUDE.md says it MAY include PII."""
    configure_logging(level="DEBUG")
    log = get_logger("test.module")
    log.debug(
        "raw_sample",
        gps_lat=47.123,
        user_email="x@y",
        power=200,
    )
    payload = _last_json_line(capsys.readouterr().out)
    assert payload["gps_lat"] == 47.123
    assert payload["user_email"] == "x@y"
    assert payload["power"] == 200


def test_configure_at_warning_drops_info_records(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """A WARNING-level configuration must not emit INFO records at all."""
    configure_logging(level="WARNING")
    log = get_logger()
    log.info("ignored_at_warning_level", power=200)
    log.warning("emitted", power=300)
    lines = [line for line in capsys.readouterr().out.splitlines() if line.strip()]
    events = [json.loads(line)["event"] for line in lines]
    assert "ignored_at_warning_level" not in events
    assert "emitted" in events


def test_configure_is_idempotent(capsys: pytest.CaptureFixture[str]) -> None:
    """Calling configure_logging twice must not duplicate output."""
    configure_logging(level="INFO")
    configure_logging(level="INFO")
    log = get_logger()
    log.info("once", power=200)
    lines = [line for line in capsys.readouterr().out.splitlines() if line.strip()]
    assert len(lines) == 1


def test_get_logger_binds_initial_values(
    capsys: pytest.CaptureFixture[str],
) -> None:
    configure_logging(level="INFO")
    log = get_logger("module.x", service="mcp-stryd", request_id="abc")
    log.info("did_thing", power=300)
    payload = _last_json_line(capsys.readouterr().out)
    assert payload["service"] == "mcp-stryd"
    assert payload["request_id"] == "abc"
    assert payload["power"] == 300


def test_get_logger_without_name(capsys: pytest.CaptureFixture[str]) -> None:
    """The no-name branch of get_logger must still produce structured output."""
    configure_logging(level="INFO")
    log = get_logger()
    log.info("anonymous", power=42)
    payload = _last_json_line(capsys.readouterr().out)
    assert payload["event"] == "anonymous"
    assert payload["power"] == 42

"""Structured JSON logging with PII redaction.

CLAUDE.md is explicit: at ``INFO`` and above, log records must not
contain GPS coordinates, FIT user-field strings, user names, or emails.
``DEBUG`` is permitted to carry more (developer-only, never enabled in
production).

The :func:`redact_pii` processor enforces this. It runs late in the
processor chain so any earlier processor that adds context still has
its keys redacted before serialization.
"""

from __future__ import annotations

import logging
import sys
from typing import TYPE_CHECKING, Any, Final, cast

import structlog

if TYPE_CHECKING:
    from structlog.types import EventDict, Processor, WrappedLogger

# Field names known to carry personal data. Add to this set rather than
# adding scrubbing logic somewhere else — one place enforces the rule.
PII_KEYS: Final[frozenset[str]] = frozenset(
    {
        "gps_lat",
        "gps_lon",
        "user_name",
        "user_email",
        "fit_user_field",
    }
)

REDACTED: Final[str] = "[REDACTED]"

_LEVEL_BY_METHOD: Final[dict[str, int]] = {
    "critical": logging.CRITICAL,
    "exception": logging.ERROR,
    "error": logging.ERROR,
    "warning": logging.WARNING,
    "warn": logging.WARNING,
    "info": logging.INFO,
    "debug": logging.DEBUG,
    "notset": logging.NOTSET,
}


def redact_pii(
    _logger: WrappedLogger,
    method_name: str,
    event_dict: EventDict,
) -> EventDict:
    """structlog processor: scrub PII keys at INFO and above.

    Keys listed in :data:`PII_KEYS` are replaced with
    :data:`REDACTED`. At DEBUG (only enabled for local dev), values
    pass through unmodified.
    """
    level = _LEVEL_BY_METHOD.get(method_name.lower(), logging.INFO)
    if level < logging.INFO:
        return event_dict
    for key in PII_KEYS:
        if key in event_dict:
            event_dict[key] = REDACTED
    return event_dict


def configure_logging(*, level: str = "INFO") -> None:
    """Initialise structlog for the running process.

    Idempotent — safe to call multiple times. Writes JSON lines to
    stdout; Docker captures, the rest is a downstream concern.
    """
    log_level_value = getattr(logging, level.upper(), None)
    log_level: int = log_level_value if isinstance(log_level_value, int) else logging.INFO

    # Route stdlib logging through structlog's formatter so libraries
    # that use `logging.getLogger(__name__)` still produce JSON.
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=log_level,
        force=True,
    )

    processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        redact_pii,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer(),
    ]

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(log_level),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(file=sys.stdout),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str | None = None, **initial_values: Any) -> structlog.stdlib.BoundLogger:
    """Return a bound structlog logger.

    A thin re-export so callers don't import structlog directly. Keyword
    arguments are bound onto the logger as initial context.
    """
    logger = structlog.get_logger(name) if name else structlog.get_logger()
    if initial_values:
        logger = logger.bind(**initial_values)
    return cast("structlog.stdlib.BoundLogger", logger)

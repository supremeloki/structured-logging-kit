from __future__ import annotations

import json
import sys
import time
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class LoggingKitError(Exception):
    pass


REDACTED_PLACEHOLDER = "***REDACTED***"
DEFAULT_REDACT_PATTERNS: tuple[str, ...] = (
    "password", "secret", "token", "api_key", "apikey",
    "authorization", "credential", "private_key",
)


class LogLevel(int, Enum):
    DEBUG = 10
    INFO = 20
    WARNING = 30
    ERROR = 40
    CRITICAL = 50

    @property
    def label(self) -> str:
        return self.name.lower()


def redact(value: Any, patterns: tuple[str, ...] = DEFAULT_REDACT_PATTERNS) -> Any:
    lowered_patterns = tuple(p.lower() for p in patterns)
    if isinstance(value, dict):
        cleaned: dict[str, Any] = {}
        for key, item in value.items():
            key_text = str(key).lower()
            if any(pattern in key_text for pattern in lowered_patterns):
                cleaned[key] = REDACTED_PLACEHOLDER
            else:
                cleaned[key] = redact(item, patterns)
        return cleaned
    if isinstance(value, list):
        return [redact(item, patterns) for item in value]
    if isinstance(value, tuple):
        return tuple(redact(item, patterns) for item in value)
    return value


@dataclass(frozen=True)
class LogRecord:
    timestamp: float
    level: LogLevel
    event: str
    fields: dict[str, Any]

    def to_dict(self, *, redact_patterns: tuple[str, ...] = DEFAULT_REDACT_PATTERNS,
                include_level_label: bool = True) -> dict[str, Any]:
        payload = redact(dict(self.fields), redact_patterns)
        record: dict[str, Any] = {
            "ts": round(self.timestamp, 3),
            "level": self.level.label if include_level_label else int(self.level),
            "event": self.event,
        }
        record.update(payload)
        return record

    def to_json(self, **options: Any) -> str:
        return json.dumps(self.to_dict(**options), sort_keys=True, default=str)


class LogSink:
    def write(self, record: LogRecord) -> None:
        raise NotImplementedError


class InMemorySink(LogSink):

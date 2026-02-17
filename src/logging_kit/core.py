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

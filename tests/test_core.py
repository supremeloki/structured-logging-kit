import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import pytest

from logging_kit import (
    InMemorySink,
    JsonlFileSink,
    LogLevel,
    StructuredLogger,
    redact,
)


class FakeClock:
    def __init__(self) -> None:
        self.now = 1000.0

    def __call__(self) -> float:
        self.now += 0.5
        return self.now


@pytest.fixture
def sink():
    return InMemorySink()


@pytest.fixture
def logger(sink):
    return StructuredLogger("ai-suite", sink=sink, clock=FakeClock())


def test_info_record_shape(logger, sink):
    logger.info("user.login", user_id=42)
    record = sink.records[0]
    payload = record.to_dict()
    assert payload["event"] == "user.login"
    assert payload["service"] == "ai-suite"
    assert payload["user_id"] == 42
    assert payload["level"] == "info"


def test_min_level_filters(logger, sink):
    logger.min_level = LogLevel.WARNING
    assert logger.debug("quiet") is None
    logger.warning("loud", reason="disk")
    assert sink.events == ("loud",)


def test_bind_context_applies_to_all_records(logger, sink):
    logger.bind(request_id="req-7")
    logger.info("step.one")
    logger.info("step.two")
    assert all(r.fields.get("request_id") == "req-7" for r in sink.records)


def test_bound_context_manager_restores(logger, sink):
    logger.bind(base="always")
    with logger.bound(temporary="scoped"):
        logger.info("inside")
    logger.info("outside")
    inside = sink.records[0].fields
    outside = sink.records[1].fields
    assert inside["temporary"] == "scoped"
    assert outside.get("temporary") is None
    assert outside["base"] == "always"


def test_unbind_removes_key(logger, sink):
    logger.bind(session="abc")
    logger.unbind("session")
    logger.info("after")
    assert "session" not in sink.records[0].fields


def test_redaction_masks_sensitive_keys(logger, sink):
    logger.info("auth.attempt",
                password="hunter2",
                api_key="sk-secret",
                username="koor")
    payload = sink.records[0].to_dict()
    assert payload["password"] == "***REDACTED***"
    assert payload["api_key"] == "***REDACTED***"
    assert payload["username"] == "koor"


def test_redaction_nested_structures():
    nested = {
        "config": {"db_password": "x", "host": "db.local"},
        "tokens": ["keep", "also-keep"],
    }
    cleaned = redact(nested)
    assert cleaned["config"]["db_password"] == "***REDACTED***"

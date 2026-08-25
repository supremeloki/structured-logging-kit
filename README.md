# logging-kit

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Structured JSON logging for AI services: level filtering, bound context, automatic secret redaction, timed blocks with slow-warning thresholds, and pluggable sinks (in-memory / JSONL file / stdout).

## 🚀 Overview

`print()` debugging doesn't survive contact with production. `logging-kit` emits one JSON object per line — timestamp, level, event name, plus whatever context you've bound — so log aggregators can query instead of grep. Secrets are **redacted automatically** by key-pattern (`password`, `api_key`, `token`, …) at serialization time, so a leaked field never leaves the process. `with logger.timed("job.run", threshold_ms=500):` turns any block into a duration record that escalates to WARNING when slow.

## ✨ Features

- **One JSON per event:** ts / level / event / service + arbitrary fields
- **Context binding:** `logger.bind(request_id=…)` applies to all records; `bound()` scopes it temporarily
- **Auto redaction:** recursive key-pattern masking before anything is written
- **Timed blocks:** `timed()` context logs `duration_ms`; over threshold → WARNING
- **Pluggable sinks:** InMemorySink (tests), JsonlFileSink (persistence), StdoutSink (containers)
- **Level filtering:** below `min_level` returns None without touching the sink
- **Injectable clock** · zero dependencies

## 🚧 Structure

```
structured-logging-kit/
├── src/logging_kit/
│   ├── __init__.py
│   └── core.py
├── tests/
│   └── test_core.py
├── README.md
└── pyproject.toml
```

## 📦 Installation

```bash
git clone https://github.com/supremeloki/structured-logging-kit.git
cd structured-logging-kit
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"
```

## 📋 Requirements

- Python 3.11+
- No runtime dependencies

## 🏃 Quick Start

```python
from logging_kit import JsonlFileSink, StructuredLogger

log = StructuredLogger(
    "ai-suite",
    sink=JsonlFileSink("logs/app.jsonl"),
    default_fields={"env": "prod"},
)

log.bind(request_id="req-42")
log.info("llm.call", model="mini-7b", tokens=350)

with log.timed("index.rebuild", threshold_ms=2000):
    rebuild()

log.error("pipeline.failed", stage="embed", password="never-logged")
# → "password": "***REDACTED***"
```

## 🔧 Error Handling

```text
LoggingKitError   # base type; sinks may subclass for IO failures
```

Bad field values never crash the logger — serialization falls back to `str()` via JSON's `default`.

## 🧪 Testing

```bash
pytest tests/ -v
```

## 📝 Code Quality

- Full type hints (`X | None` style), frozen records
- Zero comments — names carry the meaning
- Redaction verified on nested structures; context restore and level gating covered

## 📄 License

MIT — see [LICENSE](LICENSE).

## 👤 Author

**Kooroush Masoumi** - [kooroushmasoumi@gmail.com](mailto:kooroushmasoumi@gmail.com)

---

⭐ Star this repo if you find it useful!

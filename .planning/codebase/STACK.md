# Technology Stack

**Analysis Date:** 2026-03-21

## Languages

**Primary:**
- Python 3.12 - All source code in `src/`

**Secondary:**
- Not detected

## Runtime

**Environment:**
- Python 3.12 (specified in `pyproject.toml`: `~=3.12.0`)
- Virtual environment: `.venv/`

**Package Manager:**
- uv (modern Python package manager)
- Lockfile: `uv.lock` (present)

## Frameworks

**Core:**
- Pydantic - Data validation and settings management
- Flask-RESTX (via flask_restx) - REST API framework (`src/jcx/api/`)

**Testing:**
- pytest - Test framework (dev dependency in `pyproject.toml`)

**Build/Dev:**
- uv_build - Build backend
- Nuitka - Compilation to standalone executables (see `README.md`)
- Ruff - Linting and code quality (`ruff.toml`)

## Key Dependencies

**Critical:**
- rustshed - Rust-inspired patterns for Python (Option, Result, Null, etc.)
- pydantic - Data validation and BaseModel
- pydantic-extra-types - Additional Pydantic types

**Infrastructure:**
- arrow - Date/time manipulation (`src/jcx/time/`)
- redis - Redis database client (`src/jcx/db/rdb/`)
- paho-mqtt - MQTT protocol client (`src/jcx/net/mqtt/`)
- requests - HTTP client library (`src/jcx/api/dao_client.py`)
- loguru - Logging framework

**Data/Math:**
- numpy - Numerical computing (`src/jcx/m/trace.py`)
- torch - PyTorch for ML/tensor operations (`src/jcx/m/trace.py`)

**CLI:**
- typer - CLI framework (`src/jcx/bin/cx_task.py`)
- rich - Terminal formatting (used with typer)

**Utilities:**
- sh - Command execution
- parse - String parsing
- interval - Interval arithmetic
- pyjson5 - JSON5 parsing
- cattr - Structuring/unstructuring data (`src/jcx/api/_dao_item.py`)

## Configuration

**Environment:**
- No `.env` file detected
- Configuration via Pydantic BaseModel classes
- URL-based configuration (e.g., `redis://127.0.0.1/10` in `src/jcx/db/rdb/db.py`)

**Build:**
- `pyproject.toml` - Project configuration
- `ruff.toml` - Linting configuration (selects "ALL" rules, ignores specific ones)
- `uv.lock` - Dependency lock file
- No pytest config detected (uses defaults)

## Platform Requirements

**Development:**
- Python 3.12
- uv package manager
- Linux environment (`.python-version` file present)

**Production:**
- Redis server (for RedisDb functionality)
- MQTT broker (for MQTT pub/sub)
- HTTP API server (for DAO client)

---

*Stack analysis: 2026-03-21*

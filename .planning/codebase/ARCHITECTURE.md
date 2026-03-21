# Architecture

**Analysis Date:** 2026-03-21

## Pattern Overview

**Overall:** Layered Utility Library with Functional Programming Patterns

**Key Characteristics:**
- Pure Python utility library organized by functional domain
- Heavy use of Rust-inspired patterns via `rustshed` library (Option, Result types)
- Immutable data patterns using Pydantic BaseModel
- Type-safe operations with extensive use of Python type hints
- Separation of concerns: utilities, data access, networking, CLI tools

## Layers

**Utilities Layer (`src/jcx/util/`, `src/jcx/sys/`, `src/jcx/m/`, `src/jcx/text/`):**
- Purpose: Core utility functions and abstractions
- Location: `src/jcx/util/`, `src/jcx/sys/`, `src/jcx/m/`, `src/jcx/text/`
- Contains: Algorithms, file system operations, math functions, text I/O, error handling
- Depends on: `rustshed`, `loguru`, standard library
- Used by: All higher layers

**Data Access Layer (`src/jcx/db/`):**
- Purpose: Database abstractions and record management
- Location: `src/jcx/db/`
- Contains: JSON-based file database (`jdb`), Redis database (`rdb`), record definitions
- Depends on: `pydantic`, `redis`, `rustshed`, text utilities
- Used by: API layer, applications

**API Layer (`src/jcx/api/`):**
- Purpose: HTTP client abstractions for REST APIs
- Location: `src/jcx/api/`
- Contains: DAO client, task management client, configuration
- Depends on: `requests`, `typer`, data layer
- Used by: CLI tools

**Networking Layer (`src/jcx/net/`):**
- Purpose: MQTT client implementations
- Location: `src/jcx/net/mqtt/`
- Contains: MQTT publisher, subscriber, configuration
- Depends on: `paho-mqtt`

**Time Layer (`src/jcx/time/`):**
- Purpose: Time and date utilities
- Location: `src/jcx/time/`
- Contains: DateTime conversions, timers, calendar types
- Depends on: `arrow`

**UI Layer (`src/jcx/ui/`):**
- Purpose: User interface utilities
- Location: `src/jcx/ui/`
- Contains: Progress meters, keyboard input
- Depends on: `rich`

**Rust Compatibility Layer (`src/jcx/rs/`):**
- Purpose: Bridge Python and Rust patterns
- Location: `src/jcx/rs/`
- Contains: Option/Result conversions, protocol definitions
- Depends on: `rustshed`

**CLI Layer (`src/jcx/bin/`):**
- Purpose: Command-line interface tools
- Location: `src/jcx/bin/`
- Contains: Task management, file operations, DAO tools
- Depends on: `typer`, `rich`, API layer, all utility layers
- Used by: End users via installed console scripts

## Data Flow

**CLI Command Execution:**

1. User invokes CLI command (e.g., `cx_task list`)
2. Typer parses arguments and calls command handler in `src/jcx/bin/cx_*.py`
3. Command handler creates client (e.g., `TaskClient` from `src/jcx/api/`)
4. Client makes HTTP request using `requests.Session`
5. Response deserialized via Pydantic models
6. Results formatted with `rich` and displayed to user

**Database Operations:**

1. Application creates `Table` or `RedisDb` instance
2. Records are Pydantic models inheriting from `Record` or `RecordSid`
3. CRUD operations return `Result[T, Exception]` for error handling
4. JSON files stored in `jdb` use format `{id}.json`
5. Redis operations use JSON serialization via `to_json`/`from_json`

**State Management:**
- Immutable records via `clone()` method (deep copy)
- Option/Result types for null-safe and error-safe operations
- No global mutable state (except Config singleton in some CLI tools)

## Key Abstractions

**Record (`src/jcx/db/record.py`):**
- Purpose: Base class for database records
- Examples: `TaskInfo`, `StatusInfo` in `src/jcx/api/task/task_types.py`
- Pattern: Pydantic BaseModel with `id` field and `clone()` method

**Result Type (from rustshed):**
- Purpose: Error handling without exceptions
- Pattern: `Result[T, E]` with `is_ok()`, `is_err()`, `unwrap()`, `unwrap_err()`
- Used throughout: All network calls, file I/O, database operations

**Option Type (from rustshed):**
- Purpose: Null-safe operations
- Pattern: `Option[T]` with `is_null()`, `unwrap()`, `map()`
- Used throughout: Optional return values, lookups that may fail

**DAO Client Pattern:**
- Purpose: REST API client abstraction
- Examples: `DaoListClient` in `src/jcx/api/dao_client.py`
- Pattern: Base URL + table name + CRUD methods returning Result types

## Entry Points

**Console Scripts (defined in pyproject.toml):**
- `cx_rename` → `src/jcx/bin/cx_rename.py:main` - File renaming tool
- `cx_task` → `src/jcx/bin/cx_task.py:main` - Task management CLI
- `cx_dao` → `src/jcx/bin/cx_dao.py:main` - DAO operations tool
- `mv_re` → `src/jcx/bin/mv_re.py:main` - Regex-based move tool
- `rename_re` → `src/jcx/bin/rename_re.py:main` - Regex-based rename tool

**Module Entry Points:**
- `src/jcx/__init__.py` - Package initialization (empty)
- Each subpackage has `__init__.py` for module organization

## Error Handling

**Strategy:** Result types for recoverable errors, exceptions for unrecoverable errors

**Patterns:**
- Network operations: Return `Result[T, Exception]` or `Result[T, str]`
- File operations: Return `Result[T, Exception]` or `Result[T, IOError]`
- Database operations: Return `Option[T]` for missing records
- CLI commands: Use `try/except` and exit with error code

## Cross-Cutting Concerns

**Logging:** `loguru` logger used throughout, configured per module

**Validation:** Pydantic models provide automatic validation on deserialization

**Serialization:** JSON via `txt_json.py` (wraps Pydantic JSON handling)

**Type Safety:** Extensive type hints, `type` aliases for common patterns

**Concurrency:** Minimal threading support in `util/mutithread.py`

---

*Architecture analysis: 2026-03-21*

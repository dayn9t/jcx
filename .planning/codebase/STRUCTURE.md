# Codebase Structure

**Analysis Date:** 2026-03-21

## Directory Layout

```
jcx/
├── dist/                   # Build output (Nuitka compiled binaries)
├── src/
│   └── jcx/               # Main package source
│       ├── api/           # HTTP/REST client abstractions
│       │   └── task/      # Task management API client
│       ├── bin/           # CLI entry points
│       ├── common.py      # Shared constants (asset paths)
│       ├── data/          # Data processing utilities
│       ├── db/            # Database abstractions
│       │   ├── jdb/       # JSON file-based database
│       │   └── rdb/       # Redis database wrapper
│       ├── m/             # Math/statistics utilities
│       ├── net/           # Networking utilities
│       │   └── mqtt/      # MQTT client implementations
│       ├── rs/            # Rust pattern compatibility layer
│       ├── sys/           # System-level utilities (filesystem, OS)
│       ├── text/          # Text I/O and parsing
│       ├── time/          # Time/date utilities
│       └── ui/            # User interface utilities
├── tests/                 # Unit tests (mirrors src/ structure)
│   ├── db/
│   │   ├── jdb/
│   │   └── rdb/
│   ├── m/
│   ├── rs/
│   ├── sys/
│   └── util/
├── .planning/             # Planning documents (GSD framework)
├── pyproject.toml         # Project configuration
├── ruff.toml              # Linting configuration
├── README.md              # Project documentation
└── TODO.md                # Known issues and TODOs
```

## Directory Purposes

**`src/jcx/api/`:**
- Purpose: HTTP client abstractions for REST APIs
- Contains: DAO clients, task management, API configuration
- Key files: `dao_client.py`, `task/task_client.py`, `task/task_types.py`

**`src/jcx/bin/`:**
- Purpose: Command-line interface entry points
- Contains: Standalone CLI scripts using typer
- Key files: `cx_task.py`, `cx_dao.py`, `cx_rename.py`, `mv_re.py`

**`src/jcx/db/`:**
- Purpose: Database abstraction layer
- Contains: Record base classes, table implementations, variant storage
- Key files: `record.py`, `counter.py`, `ivariant.py`

**`src/jcx/db/jdb/`:**
- Purpose: JSON file-based database implementation
- Contains: Table class, variant storage, utility functions
- Key files: `table.py`, `variant.py`, `util.py`

**`src/jcx/db/rdb/`:**
- Purpose: Redis database wrapper
- Contains: RedisDb class, variant storage, counter
- Key files: `db.py`, `variant.py`, `counter.py`

**`src/jcx/util/`:**
- Purpose: General utility functions
- Contains: Algorithms, error handling, data structures, threading
- Key files: `algo.py`, `err.py`, `lict.py`, `oo.py`

**`src/jcx/sys/`:**
- Purpose: System-level operations
- Contains: Filesystem operations, OS utilities
- Key files: `fs.py`, `os_pkg.py`

**`src/jcx/text/`:**
- Purpose: Text I/O and serialization
- Contains: JSON read/write, text file operations
- Key files: `txt_json.py`, `txt_json5.py`, `io.py`

**`src/jcx/time/`:**
- Purpose: Time and date utilities
- Contains: DateTime conversions, timers, calendar types
- Key files: `dt.py`, `dt_util.py`, `timer.py`, `stop_watch.py`

**`src/jcx/m/`:**
- Purpose: Math and statistics utilities
- Contains: Number operations, sqrt, random, trace, averaging
- Key files: `number.py`, `sqrt.py`, `rand.py`, `average_meter.py`

**`src/jcx/net/`:**
- Purpose: Networking utilities
- Contains: MQTT client wrapper
- Key files: `mqtt/mqtt_c.py`, `mqtt/publisher.py`, `mqtt/subscriber.py`

**`src/jcx/rs/`:**
- Purpose: Rust-inspired pattern compatibility
- Contains: Option/Result conversions, protocol definitions
- Key files: `rs.py`, `proto.py`

**`src/jcx/ui/`:**
- Purpose: User interface utilities
- Contains: Progress display, keyboard input
- Key files: `progress_meter.py`, `key.py`

**`src/jcx/data/`:**
- Purpose: Data processing utilities
- Contains: Data splitting functions
- Key files: `split.py`

**`tests/`:**
- Purpose: Unit and integration tests
- Contains: Test files mirroring source structure
- Organization: Matches `src/jcx/` subdirectories

## Key File Locations

**Entry Points:**
- `src/jcx/bin/cx_task.py:main()` - Task management CLI
- `src/jcx/bin/cx_dao.py:main()` - Database operations CLI
- `src/jcx/bin/cx_rename.py:main()` - File renaming CLI

**Configuration:**
- `pyproject.toml` - Project metadata, dependencies, console scripts
- `ruff.toml` - Linting rules (ruff configuration)
- `.python-version` - Python version specification (3.12)

**Core Abstractions:**
- `src/jcx/db/record.py` - Record base classes
- `src/jcx/text/txt_json.py` - JSON serialization utilities
- `src/jcx/rs/rs.py` - Option/Result conversion utilities

**Testing:**
- `tests/` - All test files organized by module
- No test configuration files (uses pytest defaults)

## Naming Conventions

**Files:**
- Modules: `snake_case.py` (e.g., `txt_json.py`, `dao_client.py`)
- Test files: `{module}_test.py` (e.g., `rs_test.py`, `number_test.py`)
- CLI binaries: `cx_{name}.py` (e.g., `cx_task.py`, `cx_dao.py`)

**Directories:**
- All lowercase: `api`, `db`, `util`, `sys`, `text`, `time`, `net`
- Short names: `m` (math), `rs` (Rust), `ui` (user interface)

**Functions:**
- `snake_case`: `get_client()`, `save_txt()`, `find_first()`

**Classes:**
- `PascalCase`: `TaskClient`, `RedisDb`, `ProgressMeter`, `DaoListClient`

**Types/Type Aliases:**
- `PascalCase` for types: `Record`, `RecordSid`, `StrPath`, `Paths`
- `snake_case` for type aliases in some cases: `Real`, `Real2D`

**Constants:**
- `SCREAMING_SNAKE_CASE` or `PascalCase` for Final: `JCX_ASSERTS`

## Where to Add New Code

**New Utility Function:**
- Primary code: `src/jcx/util/` or appropriate domain subdirectory
- Tests: `tests/util/` or matching test subdirectory

**New CLI Tool:**
- Implementation: `src/jcx/bin/cx_{name}.py`
- Add to `pyproject.toml`: `[project.scripts]` section
- Tests: `tests/bin/` (create if needed)

**New Database Backend:**
- Implementation: `src/jcx/db/{backend_name}/`
- Create: `__init__.py`, main module file
- Follow pattern of `jdb/` or `rdb/` directories
- Tests: `tests/db/{backend_name}/`

**New API Client:**
- Implementation: `src/jcx/api/{service}/`
- Create: `client.py`, `types.py`, `__init__.py`
- Tests: `tests/api/{service}/`

**New Math/Statistics Function:**
- Implementation: `src/jcx/m/{module}.py`
- Tests: `tests/m/{module}_test.py`

**New Time Utility:**
- Implementation: `src/jcx/time/{module}.py`
- Tests: `tests/time/` (create if needed)

**New Networking Protocol:**
- Implementation: `src/jcx/net/{protocol}/`
- Create: `__init__.py`, client modules
- Tests: `tests/net/{protocol}/`

## Special Directories

**`dist/`:**
- Purpose: Nuitka compiled binaries
- Generated: Yes (by build process)
- Committed: No

**`.planning/`:**
- Purpose: GSD framework planning documents
- Generated: Yes (by GSD commands)
- Committed: Yes

**`.ruff_cache/`:**
- Purpose: Ruff linter cache
- Generated: Yes
- Committed: No

**`__pycache__/`:**
- Purpose: Python bytecode cache
- Generated: Yes
- Committed: No

**`.venv/`:**
- Purpose: Virtual environment
- Generated: Yes
- Committed: No

---

*Structure analysis: 2026-03-21*

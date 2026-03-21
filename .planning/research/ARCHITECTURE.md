# Architecture Research

**Domain:** Python Utility Library (Rust-style type safety patterns)
**Researched:** 2026-03-21
**Confidence:** HIGH

## Standard Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                      CLI Layer (bin/)                        │
│  cx_rename, cx_task, cx_dao, mv_re, rename_re              │
├─────────────────────────────────────────────────────────────┤
│                       API Layer (api/)                       │
│     DaoListClient, TaskClient, Configuration                │
├─────────────────────────────────────────────────────────────┤
│                   Networking Layer (net/)                    │
│         MQTT Publisher, Subscriber, Configuration           │
├─────────────────────────────────────────────────────────────┤
│                  Data Access Layer (db/)                     │
│      jdb (JSON Database), rdb (Redis), Record Types         │
├─────────────────────────────────────────────────────────────┤
│                    Time Layer (time/)                        │
│        DateTime conversions, Timers, Calendar Types         │
├─────────────────────────────────────────────────────────────┤
│                      UI Layer (ui/)                          │
│            Progress meters, Keyboard input (rich)           │
├─────────────────────────────────────────────────────────────┤
│                  Utilities Layer (util/, sys/, text/, m/)    │
│   Algorithms, File System, JSON I/O, Math, Error Handling   │
├─────────────────────────────────────────────────────────────┤
│              Rust Compatibility Layer (rs/)                  │
│            Option/Result conversions, Protocol defs         │
└─────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│                  External Dependencies                       │
│   rustshed (Option/Result), pydantic (Records), requests    │
│   redis, paho-mqtt, loguru, typer, rich, pytest             │
└─────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

| Component | Responsibility | Typical Implementation |
|-----------|----------------|------------------------|
| CLI Layer (bin/) | Command-line interface entry points | typer commands with rich output |
| API Layer (api/) | HTTP client abstractions for REST APIs | requests.Session with Result-wrapped responses |
| Networking Layer (net/) | MQTT client implementations | paho-mqtt with pub/sub patterns |
| Data Access Layer (db/) | Database abstractions and record management | jdb (file-based JSON), rdb (Redis), Pydantic models |
| Time Layer (time/) | Time and date utilities | arrow-based conversions, calendar triggers |
| UI Layer (ui/) | User interface utilities | rich progress bars, keyboard input |
| Utilities Layer (util/, sys/, text/, m/) | Core utility functions | File system ops, JSON I/O, algorithms, math |
| Rust Compatibility Layer (rs/) | Bridge Python and Rust patterns | rustshed Option/Result wrappers |

## Recommended Project Structure

```
src/jcx/
├── api/                    # HTTP client abstractions
│   ├── task/              # Task management client
│   │   ├── task_client.py
│   │   └── task_types.py
│   ├── _dao_item.py       # Single DAO item operations
│   ├── _dao_list.py       # DAO list operations
│   └── dao_client.py      # Base DAO client
├── bin/                    # CLI entry points
│   ├── cx_rename.py       # File renaming tool
│   ├── cx_task.py         # Task management CLI
│   ├── cx_dao.py          # DAO operations tool
│   ├── mv_re.py           # Regex-based move
│   └── rename_re.py       # Regex-based rename
├── db/                     # Database abstractions
│   ├── jdb/               # JSON file database
│   │   ├── table.py       # Table operations
│   │   └── variant.py     # Variant handling
│   ├── rdb/               # Redis database
│   │   └── db.py          # Redis operations
│   └── record.py          # Base Record classes
├── m/                      # Math utilities
│   ├── number.py          # Number operations
│   └── pt.py              # Point/coordinate types
├── net/                    # Networking
│   └── mqtt/              # MQTT client
│       ├── publisher.py
│       ├── subscriber.py
│       └── config.py
├── rs/                     # Rust compatibility
│   └── protocol.py        # Protocol definitions
├── sys/                    # System utilities
│   └── fs.py              # File system operations
├── text/                   # Text processing
│   ├── txt_json.py        # JSON serialization
│   └── io.py              # Text I/O
├── time/                   # Time utilities
│   ├── calendar_type.py   # Calendar types and triggers
│   └── clock_time.py      # Clock and time utilities
├── ui/                     # User interface
│   └── progress.py        # Progress indicators
└── util/                   # General utilities
    ├── algo.py            # Algorithms (list operations)
    ├── err.py             # Error handling utilities
    └── mutithread.py      # Multithreading utilities

tests/                      # Test mirror structure
├── api/
├── db/
├── net/
└── util/
```

### Structure Rationale

- **api/**: Isolated HTTP client layer for external REST API communication
- **bin/**: CLI entry points separated from library code for clear boundaries
- **db/**: Data access layer with two backends (jdb for files, rdb for Redis)
- **util/, sys/, text/, m/**: Pure utility functions with no external dependencies beyond stdlib
- **rs/**: Rust pattern compatibility layer for Option/Result conversions
- **time/**: Time handling isolated for timezone complexity containment

## Architectural Patterns

### Pattern 1: Result/Option Error Handling (Rust-style)

**What:** Use rustshed library for functional error handling without exceptions
**When to use:** All fallible operations (network, I/O, database)
**Trade-offs:** More verbose but safer than exceptions; requires unwrapping discipline

**Example:**
```python
from rustshed import Result, Ok, Err, Option, Some, Null

# Network operation returns Result
def fetch_user(user_id: int) -> Result[User, Exception]:
    response = requests.get(f"/users/{user_id}")
    if response.ok:
        return Ok(User(**response.json()))
    return Err(Exception(f"Failed to fetch: {response.status_code}"))

# Database lookup returns Option
def find_record(rid: int) -> Option[Record]:
    path = self.path(rid)
    if path.exists():
        return Some(load_json(path))
    return Null

# Safe usage pattern
result = fetch_user(1)
if result.is_ok():
    user = result.unwrap()
    # use user
else:
    show_err(result)
```

**Critical Anti-Pattern (33 instances found):**
```python
# WRONG: Panics on None/Err
user = fetch_user(1).unwrap()
record = find_record(42).unwrap()

# CORRECT: Safe unwrapping
user = fetch_user(1).unwrap_or_else(lambda e: default_user)
record = find_record(42).unwrap_or(Null)
```

### Pattern 2: Immutable Records with Pydantic

**What:** Pydantic BaseModel with deep copy for immutability
**When to use:** All database records and configuration objects
**Trade-offs:** Memory overhead from copying, but prevents mutation bugs

**Example:**
```python
from pydantic import BaseModel
from typing import Self

class Record(BaseModel):
    id: int
    name: str

    def clone(self: Self) -> Self:
        """Deep copy for immutability."""
        return self.model_copy(deep=True)

# Usage in Table class
def post(self, record: R) -> Option[R]:
    record = record.clone()  # Defensive copy
    # ... save record
    return Some(record)
```

### Pattern 3: Type Aliases for Clarity

**What:** Python 3.12+ `type` keyword for semantic type aliases
**When to use:** Union types, callable types, commonly repeated patterns
**Trade-offs:** No runtime enforcement, but improves readability

**Example:**
```python
# Current patterns in codebase
type StrPath = str | Path
type Real = int | float
type Real2D = tuple[Real, Real]
type RecordFilter = Callable[[Record], bool]
type ResultE[T] = Result[T, Exception]

# Usage
def load_file(path: StrPath) -> Result[str, IOError]:
    ...

def filter_records(records: list[Record], pred: RecordFilter) -> list[Record]:
    ...
```

### Pattern 4: Layered Dependency Direction

**What:** Strict dependency flow from top to bottom layers
**When to use:** Always - prevents circular dependencies
**Trade-offs:** May require more indirection, but keeps architecture clean

**Dependency Rules:**
```
CLI → API → Data Access → Utilities → rustshed/pydantic
CLI → Networking → Utilities
Time → Utilities
UI → Utilities
```

**Anti-Pattern:**
```python
# WRONG: Utilities importing from API layer
from jcx.api.dao_client import DaoClient  # in util/algo.py

# CORRECT: API layer imports utilities
from jcx.util.algo import list_index  # in api/dao_client.py
```

## Data Flow

### CLI Command Execution Flow

```
User invokes: cx_task list
    ↓
typer parses arguments
    ↓
cx_task.py:main() creates TaskClient
    ↓
TaskClient.get_all() → requests.Session → HTTP API
    ↓
Response → Pydantic model deserialization
    ↓
Result[list[TaskInfo], Exception]
    ↓
if result.is_ok(): rich.Table display
    ↓
Console output to user
```

### Database Operations Flow

```
Application creates Table[RecordType]
    ↓
post(record) → record.clone() → validate ID
    ↓
to_json(record) → write to {id}.json
    ↓
return Some(record) or Null

get(id) → read {id}.json → from_json()
    ↓
return Some(record) or Null
```

### Error Propagation Flow

```
Low-level operation (file I/O, network)
    ↓
Return Result[T, E] or Option[T]
    ↓
Mid-level aggregates errors
    ↓
High-level decides: recover or show_err()
    ↓
CLI: exit with error code
API: return error response
```

## Error Handling Architecture

### Current State Analysis

**Good Patterns:**
- 55+ uses of Result/Option for fallible operations
- `show_err()` utility for consistent error display
- Pydantic validation for data integrity

**Critical Issues (from CONCERNS.md):**

| Issue | Count | Severity | Fix Priority |
|-------|-------|----------|--------------|
| Unsafe `.unwrap()` calls | 33 | HIGH | Phase 1 |
| `assert` statements (runtime checks) | 23 | HIGH | Phase 1 |
| `# type: ignore` comments | 9 | MEDIUM | Phase 2 |
| Broad `except Exception` clauses | ~10 | MEDIUM | Phase 2 |

### Recommended Error Handling Patterns

#### Pattern A: Safe Unwrapping (Replace 33 .unwrap() calls)

```python
# BEFORE (unsafe)
def get_config() -> Config:
    return load_config().unwrap()  # Panics on error

# AFTER (safe)
def get_config() -> Config:
    result = load_config()
    if result.is_ok():
        return result.unwrap()
    logger.error(f"Failed to load config: {result.unwrap_err()}")
    return Config.default()
```

**Migration Strategy:**
1. Grep all `.unwrap()` and `.unwrap_err()` calls
2. Classify by context (can fail safely vs. must fail hard)
3. Replace safe cases with `unwrap_or()`, `unwrap_or_else()`, or match patterns
4. For must-fail cases, replace `assert` with explicit `raise` or `Err()`

#### Pattern B: Replace Assert with Proper Error Handling

```python
# BEFORE (assert disabled with -O flag)
assert url.startswith("redis://"), f"Invalid URL: {url}"

# AFTER (explicit validation)
if not url.startswith("redis://"):
    return Err(ValueError(f"Invalid Redis URL: {url}"))
```

**Affected Files:**
- `src/jcx/db/rdb/db.py:26-31` - Redis URL parsing
- 23 total assert statements need review

#### Pattern C: Specific Exception Catching

```python
# BEFORE (broad catch)
try:
    response = self.session.get(url)
except Exception as e:
    return Err(e)

# AFTER (specific catches)
try:
    response = self.session.get(url, timeout=30)
except requests.Timeout:
    return Err(TimeoutError(f"Request to {url} timed out"))
except requests.ConnectionError as e:
    return Err(ConnectionError(f"Failed to connect: {e}"))
except requests.RequestException as e:
    return Err(e)
```

**Affected Files:**
- `src/jcx/api/dao_client.py`
- `src/jcx/bin/cx_task.py`
- `src/jcx/bin/cx_dao.py`

### Error Handling Migration Checklist

For each module during refactoring:
- [ ] Identify all `.unwrap()` calls (use `grep -rn "\.unwrap()" src/`)
- [ ] Classify: safe default exists (use `unwrap_or`) vs. must fail (use explicit error)
- [ ] Replace `assert` with `Result` return or explicit `raise`
- [ ] Narrow `except Exception` to specific exception types
- [ ] Add logging for all error paths
- [ ] Test error handling paths explicitly

## Testing Architecture

### Recommended Test Structure

```
tests/
├── conftest.py            # Shared fixtures
├── unit/                  # Unit tests (fast, isolated)
│   ├── util/
│   │   └── test_algo.py
│   ├── db/
│   │   ├── test_record.py
│   │   └── test_table.py
│   └── text/
│       └── test_txt_json.py
├── integration/           # Integration tests (slower, real deps)
│   ├── test_jdb.py       # Real file I/O
│   └── test_rdb.py       # Real Redis (or mock)
└── e2e/                   # End-to-end (slowest, full stack)
    └── test_cli.py       # CLI commands
```

### Testing Patterns

#### Pattern A: Pytest with Mocking (Current)

```python
from unittest.mock import patch, MagicMock
from pytest import fixture

@fixture
def mock_session():
    with patch("requests.Session") as mock:
        yield mock

def test_get_all_success(mock_session):
    # Arrange
    client = DaoListClient("http://api")
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.json.return_value = [{"id": 1, "name": "Test"}]
    mock_session.return_value.get.return_value = mock_response

    # Act
    result = client.get_all(User, "users")

    # Assert
    assert result.is_ok()
    users = result.unwrap()
    assert len(users) == 1
    assert users[0].name == "Test"
```

#### Pattern B: Fixture-Based Testing (Recommended for Database)

```python
# tests/conftest.py
import pytest
from pathlib import Path
import tempfile

@pytest.fixture
def temp_db_dir():
    """Temporary directory for file-based database tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)

@pytest.fixture
def sample_record():
    """Sample record for testing."""
    return User(id=1, name="Test User")

# tests/db/test_table.py
def test_post_record(temp_db_dir, sample_record):
    # Arrange
    table = Table[User](temp_db_dir, User)

    # Act
    result = table.post(sample_record)

    # Assert
    assert result.is_some()
    saved = result.unwrap()
    assert saved.id == sample_record.id
    assert saved.name == sample_record.name
```

#### Pattern C: Property-Based Testing (For Complex Logic)

```python
from hypothesis import given, strategies as st

@given(st.integers(min_value=1, max_value=1000000))
def test_record_id_always_positive(rid):
    """Property: Record IDs should always be positive after post."""
    table = Table[User](temp_dir, User)
    record = User(id=rid, name="Test")

    result = table.post(record)

    assert result.is_some()
    assert result.unwrap().id > 0
```

### Coverage Requirements

**Minimum Coverage: 80%** (per testing.md rules)

**Coverage Configuration:**
```toml
# pyproject.toml
[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "--cov=src/jcx --cov-report=term-missing --cov-fail-under=80"

[tool.coverage.run]
source = ["src/jcx"]
omit = ["*/tests/*", "*/__pycache__/*"]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
]
```

### Test Coverage Gaps to Address

From CONCERNS.md, these areas need tests:
1. **Weekday filtering in calendar triggers** (`src/jcx/time/calendar_type.py:53`)
2. **File time utilities** (`src/jcx/sys/fs.py:320-332`)
3. **Global state in multithread** (`src/jcx/util/mutithread.py`)
4. **Integration tests for API flows** (`src/jcx/api/`)
5. **Concurrent database access** (`src/jcx/db/jdb/`)
6. **MQTT pub/sub** (`src/jcx/net/mqtt/`)

### Testing Anti-Patterns to Avoid

**Anti-Pattern 1: Mocking Everything**
```python
# WRONG: Over-mocking makes tests brittle
@patch("jcx.db.jdb.table.Path")
@patch("jcx.db.jdb.table.load_json")
@patch("jcx.db.jdb.table.save_json")
def test_table_operations(mock_save, mock_load, mock_path):
    # Test only verifies mocks, not actual behavior
```

**Correct Approach:**
```python
# CORRECT: Use real file I/O with temp directories
def test_table_operations(temp_db_dir):
    table = Table[User](temp_db_dir, User)
    # Test real behavior
```

**Anti-Pattern 2: Ignoring Error Paths**
```python
# WRONG: Only tests happy path
def test_get_record():
    result = table.get(1)
    assert result.is_some()  # What if record doesn't exist?
```

**Correct Approach:**
```python
# CORRECT: Test both success and failure
def test_get_record_exists():
    result = table.get(existing_id)
    assert result.is_some()

def test_get_record_not_found():
    result = table.get(99999)
    assert result.is_null()
```

## Scaling Considerations

| Scale | Architecture Adjustments |
|-------|--------------------------|
| 0-1k records | Current jdb (file-based JSON) is sufficient |
| 1k-100k records | Add pagination to Table operations; consider caching |
| 100k+ records | Migrate from jdb to SQLite or PostgreSQL; implement Redis caching |

### Scaling Priorities

1. **First bottleneck:** File-based database loads entire dataset into memory
   - Fix: Add pagination to `Table.get_all()` and lazy loading
   - When: When record count exceeds 10,000

2. **Second bottleneck:** No connection pooling for HTTP client
   - Fix: Configure HTTPAdapter with pool size and retry logic
   - When: When concurrent API calls exceed 10

3. **Third bottleneck:** Synchronous I/O blocks event loop
   - Fix: Migrate to async/await with aiofiles and aiohttp
   - When: When response time exceeds 1s for 100 concurrent requests
   - Note: Out of scope for current refactoring (per PROJECT.md)

## Anti-Patterns

### Anti-Pattern 1: Global Mutable State

**What people do:** Use module-level globals without synchronization
**Why it's wrong:** Race conditions in multithreaded environments
**Do this instead:** Use thread-local storage or pass state explicitly

**Example from codebase:**
```python
# src/jcx/util/mutithread.py
num = 0  # Global mutable state
# lock = Lock()  # Commented out!

def change_num():
    global num
    # with lock:  # Commented out!
    num += 1  # Race condition!
```

**Fix:**
```python
from threading import Lock

num = 0
lock = Lock()

def change_num():
    global num
    with lock:
        num += 1
```

### Anti-Pattern 2: Assert for Runtime Validation

**What people do:** Use `assert` for data validation
**Why it's wrong:** Assertions disabled with `python -O` flag in production
**Do this instead:** Explicit validation with proper error types

**Example:**
```python
# src/jcx/db/rdb/db.py:26-31
assert url.startswith("redis://"), f"Invalid URL: {url}"
```

**Fix:**
```python
if not url.startswith("redis://"):
    raise ValueError(f"Invalid Redis URL: {url}")
# or
if not url.startswith("redis://"):
    return Err(ValueError(f"Invalid Redis URL: {url}"))
```

### Anti-Pattern 3: Unsafe Unwrapping

**What people do:** Call `.unwrap()` on Option/Result without checking
**Why it's wrong:** Panics on None/Err, crashing the application
**Do this instead:** Use safe unwrapping with defaults or explicit error handling

**33 instances found in codebase - critical priority**

### Anti-Pattern 4: Broad Exception Catching

**What people do:** `except Exception as e` catches everything
**Why it's wrong:** Masks programming errors (KeyError, AttributeError) vs expected errors
**Do this instead:** Catch specific exception types

### Anti-Pattern 5: Commented-Out Code with TODOs

**What people do:** Leave commented code with TODO instead of implementing
**Why it's wrong:** Dead code that rots; TODOs without owners never get done
**Do this instead:** Create tracked issues or implement immediately

**Examples from codebase:**
- `src/jcx/sys/fs.py:320-332` - Commented file time utility
- `src/jcx/time/calendar_type.py:53` - Weekday checking TODO

## Integration Points

### External Services

| Service | Integration Pattern | Notes |
|---------|---------------------|-------|
| REST APIs | DaoListClient with requests.Session | Add timeout (currently missing) |
| Redis | rdb/db.py with redis-py | URL parsing uses assert (fix needed) |
| MQTT | paho-mqtt in net/mqtt/ | Type stubs missing (# type: ignore) |
| File System | sys/fs.py with pathlib | No streaming for large files |

### Internal Boundaries

| Boundary | Communication | Notes |
|----------|---------------|-------|
| CLI ↔ API | Function calls | Clear boundary, good separation |
| API ↔ Data Access | Result types | Good error propagation |
| Data Access ↔ Utilities | Direct calls | Utilities should not import from upper layers |
| Time ↔ Utilities | Direct calls | Time module isolated, good |
| All ↔ rustshed | Type imports | Core dependency, used everywhere |

## Refactor Order Recommendations

Based on dependency analysis and risk assessment:

### Phase 1: Foundation (Critical Fixes)

**Goal:** Eliminate crash risks and establish safe patterns

**Order:**
1. **Fix unsafe `.unwrap()` calls (33 instances)**
   - Start from utilities layer (util/, sys/, text/)
   - Move up to data access (db/)
   - Then API layer (api/)
   - Finally CLI (bin/)
   - Rationale: Lower layers used by upper layers; fix from bottom up

2. **Replace assert statements (23 instances)**
   - Priority: `src/jcx/db/rdb/db.py:26-31` (security risk)
   - Then: Other runtime validation points
   - Rationale: Assert disabled in production; critical for reliability

3. **Fix MQTT subscriber test hang**
   - File: `tests/net/subscriber_test.py:13`
   - Rationale: Blocking test prevents CI/CD

**Estimated effort:** 3-5 days
**Risk:** LOW - Localized changes, well-defined fixes

### Phase 2: Quality Improvements

**Goal:** Improve error handling and test coverage

**Order:**
1. **Narrow exception handling**
   - Files: `src/jcx/api/dao_client.py`, `src/jcx/bin/cx_task.py`, `src/jcx/bin/cx_dao.py`
   - Replace `except Exception` with specific types
   - Add timeouts to HTTP requests

2. **Add missing tests**
   - Calendar weekday filtering (`src/jcx/time/calendar_type.py:53`)
   - File time utilities (`src/jcx/sys/fs.py:320-332`)
   - Integration tests for API layer

3. **Fix type ignore comments (9 instances)**
   - Add proper type stubs or fix typing issues
   - Priority: paho-mqtt type stubs

4. **Implement logging configuration**
   - Centralized loguru config
   - Structured logging format

**Estimated effort:** 5-7 days
**Risk:** MEDIUM - May reveal hidden bugs

### Phase 3: Performance & Scalability

**Goal:** Address performance bottlenecks

**Order:**
1. **Add HTTP connection pooling**
   - Configure HTTPAdapter in `src/jcx/api/dao_client.py`
   - Add retry logic with exponential backoff

2. **Implement streaming for large files**
   - Files: `src/jcx/sys/fs.py`, `src/jcx/text/txt_json.py`
   - Chunked JSON parsing for large datasets

3. **Fix global mutable state**
   - File: `src/jcx/util/mutithread.py`
   - Add proper synchronization or remove globals

**Estimated effort:** 3-4 days
**Risk:** LOW - Performance improvements don't change behavior

### Phase 4: Tech Debt Cleanup

**Goal:** Resolve incomplete implementations

**Order:**
1. **Complete calendar weekday checking**
   - File: `src/jcx/time/calendar_type.py:53`
   - Implement weekday filtering in `CalendarTrigger.check()`

2. **Implement file time utility**
   - File: `src/jcx/sys/fs.py:320-332`
   - Use Iterator pattern as suggested in TODO

3. **Dynamic API model generation**
   - Files: `src/jcx/api/_dao_item.py:62`, `src/jcx/api/_dao_list.py:100`
   - Consider migration to FastAPI (out of current scope, but document)

4. **Complete arrow migration or removal**
   - File: `tests/text/txt_json_test.py:21`
   - Migrate to datetime or pendulum

**Estimated effort:** 4-6 days
**Risk:** MEDIUM - May require API changes

### Phase 5: Missing Features

**Goal:** Add critical missing infrastructure

**Order:**
1. **API documentation**
   - Enable Swagger UI for Flask-RESTX
   - Or document migration path to FastAPI

2. **Test coverage reporting**
   - Add pytest-cov configuration
   - Set up coverage badges

3. **Secret management**
   - Add python-dotenv
   - Create `.env.example` template

4. **Input validation framework**
   - Use Pydantic for all CLI inputs
   - Centralize validation logic

**Estimated effort:** 3-4 days
**Risk:** LOW - Additive changes

## Dependencies at Risk

| Dependency | Risk Level | Mitigation |
|------------|------------|------------|
| Flask-RESTX | HIGH | Plan migration to FastAPI (out of scope for now) |
| rustshed | MEDIUM | Monitor maintenance; consider native typing alternative |
| arrow | HIGH | Complete migration to datetime or pendulum |
| paho-mqtt | LOW | Add type stubs to fix `# type: ignore` |

## Sources

- Python Application Architecture Patterns: https://realpython.com/python-application-layouts/ (HIGH confidence)
- Error Handling Best Practices: https://docs.python.org/3/tutorial/errors.html (HIGH confidence - official docs)
- Pytest Testing Best Practices: https://docs.pytest.org/en/stable/goodpractices.html (HIGH confidence - official docs)
- Pydantic Documentation: https://docs.pydantic.dev/latest/ (HIGH confidence - official docs)
- Rust-style Error Handling in Python: https://lexi-lambda.github.io/blog/2019/11/05/parse-don-t-validate/ (MEDIUM confidence - community resource)
- Test Coverage Best Practices: https://coverage.readthedocs.io/ (HIGH confidence - official docs)
- Codebase Analysis: `.planning/codebase/ARCHITECTURE.md`, `.planning/codebase/CONCERNS.md` (HIGH confidence - direct analysis)

---

*Architecture research for: Python utility library with Rust-style type safety*
*Researched: 2026-03-21*

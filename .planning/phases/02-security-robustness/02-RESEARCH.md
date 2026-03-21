# Phase 2: Security & Robustness - Research

**Researched:** 2026-03-21
**Domain:** Python HTTP client configuration, exception handling, input validation, Result/Option patterns
**Confidence:** HIGH

## Summary

This phase addresses security and robustness concerns in the jcx library, focusing on six specific requirements: HTTP connection timeouts, specific exception handling, CLI input validation, Redis URL validation, calendar weekday checking, and file time iterator implementation.

The codebase already uses rustshed's Result/Option types extensively, but has several patterns that need improvement:
- **HTTP client** (`dao_client.py`): No timeout configuration, uses `requests.Session` without pool limits
- **Exception handling**: 10+ locations using broad `except Exception` instead of specific types
- **CLI tools**: Input validation is manual, not using Pydantic models for validation
- **Redis URL**: Uses `assert` for URL validation in `db.py:26,31`
- **Calendar weekday**: `CalendarTrigger.check()` has incomplete weekday checking (TODO comment)
- **File time utility**: Commented-out code at `fs.py:320-332` shows intended Iterator pattern

**Primary recommendation:** Use requests `Timeout` and `HTTPAdapter` for connection management; replace broad exception handlers with specific types from requests library; leverage Pydantic for CLI input validation.

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| requests | 2.x | HTTP client | Standard Python HTTP library, already in use |
| rustshed | latest | Result/Option types | Already adopted for Rust-style error handling |
| pydantic | 2.x | Data validation | Already in use for records and models |
| urllib.parse | stdlib | URL parsing | Standard library for URL validation |

### Supporting
| Library | Purpose | When to Use |
|---------|---------|-------------|
| requests.adapters.HTTPAdapter | Connection pooling | For pool size limits in DaoListClient |
| requests.exceptions | Specific exception types | Replace broad `except Exception` |
| pydantic.ValidationError | Input validation errors | CLI input validation |
| arrow | Date/time handling | Calendar weekday checking |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| requests.Session | httpx | httpx is async-first; requests is synchronous and already integrated |
| manual exception mapping | tenacity | Tenacity adds retry logic; overkill for simple exception narrowing |

## Architecture Patterns

### Pattern 1: HTTP Client Timeout Configuration

**What:** Configure timeouts and pool limits on requests Session
**When to use:** All HTTP clients that make external API calls
**Example:**
```python
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

class DaoListClient:
    def __init__(self, base_url: str, timeout: float = 30.0, pool_connections: int = 10, pool_maxsize: int = 10):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()

        # Configure connection pooling
        adapter = HTTPAdapter(
            pool_connections=pool_connections,
            pool_maxsize=pool_maxsize,
            max_retries=Retry(total=3, backoff_factor=0.1)
        )
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        self.headers = {"Content-Type": "application/json"}

    def get_all(self, ...) -> ResultE[list[R]]:
        try:
            response = self.session.get(url, params=params, headers=self.headers, timeout=self.timeout)
            # ...
```

**Source:** requests official documentation

### Pattern 2: Specific Exception Handling

**What:** Catch specific requests exceptions instead of broad Exception
**When to use:** All HTTP operations in dao_client.py and CLI tools

**Exception hierarchy for requests:**
```python
from requests.exceptions import (
    RequestException,      # Base class for all requests exceptions
    ConnectionError,       # Network connectivity issues
    Timeout,               # Request timeout
    HTTPError,             # HTTP 4xx/5xx responses (from raise_for_status)
    TooManyRedirects,      # Redirect loop
    JSONDecodeError,       # Invalid JSON response (from response.json())
)

# Replace:
except Exception as e:
    return Err(f"Failed: {e}")

# With:
except Timeout:
    return Err("Request timed out")
except ConnectionError:
    return Err("Failed to connect to server")
except HTTPError as e:
    return Err(f"HTTP error: {e.response.status_code}")
except JSONDecodeError:
    return Err("Invalid JSON response")
except RequestException as e:
    return Err(f"Request failed: {e}")
```

### Pattern 3: Pydantic Input Validation for CLI

**What:** Define Pydantic models for CLI input and validate before processing
**When to use:** CLI tools that accept structured input (cx_task, cx_dao)

**Example:**
```python
from pydantic import BaseModel, field_validator, ValidationError

class TaskCreateInput(BaseModel):
    name: str
    task_type: int
    data: str
    desc: str | None = None

    @field_validator('task_type')
    @classmethod
    def validate_task_type(cls, v):
        if v < 0:
            raise ValueError('task_type must be non-negative')
        return v

@tasks_app.command("create")
def create_task(
    name: str = typer.Option(...),
    task_type: int = typer.Option(...),
    data: str = typer.Option(...),
    desc: str | None = typer.Option(None),
):
    try:
        validated_input = TaskCreateInput(name=name, task_type=task_type, data=data, desc=desc)
    except ValidationError as e:
        rprint(f"[red]Input validation failed: {e}[/red]")
        sys.exit(1)

    # Use validated_input.name, validated_input.task_type, etc.
```

### Pattern 4: Result/Option for URL Validation

**What:** Replace assert with Result-returning validation function
**When to use:** Redis URL parsing in db.py

**Example:**
```python
from rustshed import Result, Ok, Err
from urllib.parse import urlparse
import re

def parse_redis_url(url: str) -> Result[tuple[str, int, int], str]:
    """Parse Redis URL and return (host, port, db_num) or error message.

    Expected format: redis://host:port/db_num
    Example: redis://127.0.0.1:6379/10
    """
    try:
        uri = urlparse(url)
        if uri.scheme != "redis":
            return Err(f"Invalid Redis URL scheme: expected 'redis://', got '{uri.scheme}://'")

        host = uri.hostname or "localhost"
        port = uri.port or 6379

        p = re.compile(r"/(\d+)")
        m = p.match(uri.path)
        if not m:
            return Err(f"Invalid Redis URL path: expected '/<db_num>', got '{uri.path}'")

        db_num = int(m.groups()[0])
        return Ok((host, port, db_num))
    except Exception as e:
        return Err(f"Failed to parse Redis URL: {e}")

# Usage:
def __init__(self, url: str):
    result = parse_redis_url(url)
    if result.is_err():
        raise ValueError(result.unwrap_err())

    host, port, db_num = result.unwrap()
    self._db = redis.Redis(host=host, port=port, db=db_num, decode_responses=True)
```

### Anti-Patterns to Avoid

- **Bare except or except Exception without re-raise**: Hides bugs and system exceptions
- **assert for runtime validation**: Removed in optimized Python (-O flag)
- **No timeout on HTTP requests**: Can hang indefinitely
- **Mutable global state for time iteration**: Use Iterator pattern instead

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Connection pooling | Custom pool manager | `HTTPAdapter` with `pool_connections`/`pool_maxsize` | Battle-tested, handles edge cases |
| Request retries | Custom retry loop | `urllib3.Retry` with `HTTPAdapter` | Exponential backoff, status code filtering |
| URL validation | Regex-only validation | `urllib.parse.urlparse` + targeted checks | Handles edge cases like IPv6, auth |
| Weekday calculation | Manual date math | `arrow` or `datetime.weekday()` | Handles DST, locale correctly |

**Key insight:** Python's standard library and requests already provide robust solutions for connection management and URL parsing.

## Common Pitfalls

### Pitfall 1: Missing Timeout Causes Indefinite Hangs

**What goes wrong:** HTTP requests without timeout hang indefinitely when server is unresponsive, blocking the entire application.
**Why it happens:** requests defaults to no timeout; developers assume network is always responsive.
**How to avoid:** Always specify timeout on all HTTP requests:
```python
# BAD
response = requests.get(url)

# GOOD
response = requests.get(url, timeout=30.0)
```
**Warning signs:** API calls in production that never return; thread pool exhaustion; connection pool full errors.

### Pitfall 2: Broad Exception Hides Root Cause

**What goes wrong:** `except Exception` catches `KeyboardInterrupt`, `SystemExit`, and other critical exceptions, making debugging impossible.
**Why it happens:** Quick fix during development becomes production code.
**How to avoid:** Catch specific exceptions; if broad catch is needed, re-raise after logging:
```python
try:
    operation()
except SpecificError as e:
    handle_error(e)
except Exception as e:
    logger.exception("Unexpected error")
    raise  # Re-raise
```
**Warning signs:** Debugging sessions with no stack trace; errors logged but not visible in monitoring.

### Pitfall 3: Assert Removed in Production

**What goes wrong:** `assert url.startswith("redis://")` works in development but silently skips validation when Python runs with `-O` optimization flag.
**Why it happens:** assert is for debugging invariants, not runtime validation.
**How to avoid:** Use explicit validation:
```python
# BAD
assert condition, "error message"

# GOOD
if not condition:
    raise ValueError("error message")
# or
if not condition:
    return Err("error message")
```
**Warning signs:** Production logs showing invalid data that should have been rejected; assert statements in non-test files.

### Pitfall 4: Mutable Iterator State

**What goes wrong:** Using global mutable state for iterator (like `_file_now` in commented code) causes unexpected behavior in concurrent usage and makes testing difficult.
**Why it happens:** Quick prototype becomes permanent solution.
**How to avoid:** Use proper Iterator pattern with encapsulated state:
```python
from collections.abc import Iterator
from arrow import Arrow

class FileTimeIterator(Iterator[Arrow]):
    """Iterator that yields sequential timestamps for file naming."""

    def __init__(self, start_time: Arrow):
        self._current = start_time

    def __next__(self) -> Arrow:
        result = self._current
        self._current = self._current.shift(seconds=1)
        return result
```
**Warning signs:** Global variables modified during iteration; tests failing when run in parallel; unpredictable iteration order.

## Code Examples

### HTTP Client with Full Configuration

```python
from typing import Any, TypeVar
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import requests
from rustshed import Err, Ok, Result
from requests.exceptions import Timeout, ConnectionError, HTTPError, RequestException

R = TypeVar("R", bound="RecordSid")

class DaoListClient:
    """HTTP client with configurable timeouts and connection pooling."""

    DEFAULT_TIMEOUT = 30.0
    DEFAULT_POOL_CONNECTIONS = 10
    DEFAULT_POOL_MAXSIZE = 10

    def __init__(
        self,
        base_url: str,
        *,
        timeout: float = DEFAULT_TIMEOUT,
        pool_connections: int = DEFAULT_POOL_CONNECTIONS,
        pool_maxsize: int = DEFAULT_POOL_MAXSIZE,
        retry_total: int = 3,
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()

        retry_strategy = Retry(
            total=retry_total,
            backoff_factor=0.1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(
            pool_connections=pool_connections,
            pool_maxsize=pool_maxsize,
            max_retries=retry_strategy,
        )
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        self.headers = {"Content-Type": "application/json"}

    def get_all(self, record_type: type[R], table_name: str, params: dict[str, Any] | None = None) -> Result[list[R], str]:
        try:
            url = f"{self.base_url}/{table_name}"
            response = self.session.get(url, params=params, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            data_list = response.json()
            records = [record_type(**item) for item in data_list]
            return Ok(records)
        except Timeout:
            return Err(f"Request timed out after {self.timeout}s")
        except ConnectionError as e:
            return Err(f"Connection failed: {e}")
        except HTTPError as e:
            return Err(f"HTTP error {e.response.status_code}: {e}")
        except RequestException as e:
            return Err(f"Request failed: {e}")
```

### Calendar Weekday Checking

```python
from pydantic import BaseModel, ConfigDict, field_validator
from typing import Literal

Weekday = Literal[0, 1, 2, 3, 4, 5, 6]  # Monday=0, Sunday=6

class CalendarTrigger(BaseModel):
    """Calendar trigger with weekday filtering."""

    model_config = ConfigDict(frozen=True)

    periods: "ClockPeriods"
    weekdays: list[Weekday] | None = None  # None = all days allowed

    @field_validator('weekdays', mode='before')
    @classmethod
    def validate_weekdays(cls, v):
        if v is not None:
            if not all(0 <= d <= 6 for d in v):
                raise ValueError('weekdays must be 0-6 (Mon-Sun)')
        return v

    def check(self, clock_time: "ClockTime") -> bool:
        """Check if time meets calendar trigger conditions."""
        # Period check
        if self.periods:
            ok = any(clock_time in p for p in self.periods)
            if not ok:
                return False

        # Weekday check
        if self.weekdays is not None:
            # Convert clock_time to datetime for weekday check
            dt = clock_time.to_datetime()
            if dt.weekday() not in self.weekdays:
                return False

        return True
```

### File Time Iterator Pattern

```python
from collections.abc import Iterator
from arrow import Arrow
from pathlib import Path

class FileTimeIterator(Iterator[Path]):
    """Iterator that generates sequential timestamp-based file paths."""

    def __init__(self, base_path: Path, start_time: Arrow, ext: str = ".jpg"):
        self._base_path = base_path
        self._current = start_time
        self._ext = ext

    def __next__(self) -> Path:
        """Generate next file path with sequential timestamp."""
        filename = time_to_file(self._current, self._ext)
        path = self._base_path / filename
        self._current = self._current.shift(seconds=1)
        return path

    def peek(self) -> Path:
        """Get current path without advancing."""
        filename = time_to_file(self._current, self._ext)
        return self._base_path / filename


# Usage:
def rename_files_with_time(src_files: list[Path], start_time: Arrow) -> list[Path]:
    """Rename files with sequential timestamps."""
    iterator = FileTimeIterator(src_files[0].parent, start_time)
    return [next(iterator) for _ in src_files]
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| No timeout on requests | Always specify timeout | Industry standard since ~2015 | Prevents hangs |
| `except Exception` | Specific exception types | Python best practice | Better error handling |
| `assert` for validation | Explicit validation with Result/raise | Always wrong but common | Works in optimized mode |
| Global mutable state | Iterator pattern | Clean code principle | Thread-safe, testable |

**Deprecated/outdated:**
- `assert` for runtime validation: Use explicit `if/raise` or `Result`
- Bare `except:` or `except Exception:` without re-raise: Always use specific exceptions

## Open Questions

1. **Should we make timeout/pool settings configurable via environment variables?**
   - What we know: Current implementation has no configuration
   - What's unclear: User requirements for tuning these values
   - Recommendation: Add optional constructor parameters with sensible defaults; environment variable support can be added later if needed

2. **What specific weekdays should CalendarTrigger support?**
   - What we know: The TODO comment suggests weekday filtering is needed
   - What's unclear: The exact data model (list of weekdays? weekday range? cron-like expression?)
   - Recommendation: Start with simple list of weekdays (0-6), can extend to more complex patterns later

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest |
| Config file | `pyproject.toml` ([tool.pytest.ini_options]) |
| Quick run command | `pytest tests/ -x -v --ignore=tests/net/subscriber_test.py` |
| Full suite command | `pytest tests/ -v` |

### Phase Requirements -> Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| FIX-05 | Calendar weekday checking | unit | `pytest tests/time/calendar_type_test.py -v` | Partial - needs weekday tests |
| FIX-06 | File time iterator | unit | `pytest tests/sys/fs_test.py -v` | No - needs iterator tests |
| SEC-01 | HTTP timeouts/pool limits | unit | `pytest tests/api/test_dao_list_client.py -v` | Yes - existing tests |
| SEC-02 | Specific exception types | unit | `pytest tests/api/test_dao_list_client.py -v` | Yes - existing tests |
| SEC-03 | CLI input validation | integration | `pytest tests/ -k "cli or task" -v` | Partial - needs validation tests |
| SEC-04 | Redis URL validation | unit | `pytest tests/db/ -v` | No - needs db.py tests |

### Sampling Rate
- **Per task commit:** `pytest tests/ -x --ignore=tests/net/subscriber_test.py`
- **Per wave merge:** `pytest tests/ -v`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `tests/time/calendar_type_test.py` - add weekday filtering tests
- [ ] `tests/sys/fs_test.py` - add FileTimeIterator tests
- [ ] `tests/db/rdb/db_test.py` - add Redis URL parsing tests (may need mock)
- [ ] `tests/api/test_cli_validation.py` - add CLI input validation tests

## Sources

### Primary (HIGH confidence)
- requests documentation - HTTP client configuration, timeout, HTTPAdapter
- Python stdlib urllib.parse - URL parsing
- rustshed library - Result/Option patterns (already in codebase)
- Pydantic v2 documentation - validation patterns

### Secondary (MEDIUM confidence)
- Existing codebase patterns in `src/jcx/` - Result/Option usage, Pydantic models
- Existing tests in `tests/api/test_dao_list_client.py` - mocking patterns

### Tertiary (LOW confidence)
- None - all recommendations based on official documentation and existing patterns

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - all libraries already in use or stdlib
- Architecture: HIGH - patterns established in existing codebase
- Pitfalls: HIGH - well-documented Python best practices

**Research date:** 2026-03-21
**Valid until:** 30 days - stable patterns, unlikely to change significantly

---

## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| FIX-05 | Complete calendar weekday checking in CalendarTrigger.check() | Pattern 2 shows weekday field addition and check implementation using datetime.weekday() |
| FIX-06 | Implement file time utility using Iterator pattern | Pattern 4 and FileTimeIterator example show complete implementation |
| SEC-01 | Add HTTP connection timeouts and pool limits to dao_client.py | Pattern 1 shows HTTPAdapter with pool_connections, pool_maxsize, and timeout configuration |
| SEC-02 | Replace broad except Exception with specific exception types (10 locations) | Pattern 2 shows requests.exceptions hierarchy and specific catch blocks |
| SEC-03 | Add input validation to CLI tools using Pydantic models | Pattern 3 shows Pydantic model for CLI input with validators |
| SEC-04 | Replace Redis URL assert with proper Result/Option error handling | Pattern 4 shows parse_redis_url function returning Result tuple |

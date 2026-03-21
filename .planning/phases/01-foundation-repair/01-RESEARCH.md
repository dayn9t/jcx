# Phase 1: Foundation Repair - Research

**Researched:** 2026-03-21
**Domain:** Python error handling patterns, Pydantic v2 migration, pytest integration testing
**Confidence:** HIGH

## Summary

Phase 1 focuses on eliminating crash risks from unsafe `.unwrap()` patterns and repairing broken tests. The codebase uses `rustshed` library for Rust-style error handling with `Result[T, E]` and `Option[T]` types. There are 33 `.unwrap()` calls in source code (24 files) and 50 additional calls in tests that need review. Pydantic v2 migration requires updating 4 files with `class Config:` patterns. The MQTT test hang is caused by `loop_forever()` blocking and should be converted to an integration test.

**Primary recommendation:** Use existing rustshed patterns (`unwrap_or()`, `unwrap_or_else()`, `Result`/`Option` return types) consistently. For Pydantic, migrate to `model_config = ConfigDict(...)`. Mark MQTT test with `@pytest.mark.integration`.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Unwrap Replacement Strategy:**
- **Primary approach**: Modify function signatures to return `Result[T, E]` or `Option[T]`, letting callers handle errors
- **When signature cannot change**: Preserve panic behavior but add detailed error messages using `.expect("detailed message")`
- **Signature changes**: Allowed - no backward compatibility requirement, follow rustshed style
- **Pattern selection by context**:
  - Core business logic → Return Result/Option
  - UI display/logging → `unwrap_or(default)` with silent fallback
  - Unrecoverable errors → `.expect()` with clear message

**Assert Replacement Strategy:**
- **Decision**: Skip assert replacement in Phase 1
- **Rationale**: Asserts are working as intended; reduces scope; can be addressed later if needed
- **Impact**: FIX-02 removed from Phase 1 scope

**MQTT Test Fix:**
- **Approach**: Mark as integration test, skip by default
- **Implementation**:
  - Add `@pytest.mark.integration` decorator to `tests/net/subscriber_test.py`
  - Configure pytest to skip integration tests by default
  - Run with `pytest -m integration` when needed
- **Root cause**: `dispatch_msg()` uses `loop_forever()` which blocks indefinitely

**Pydantic v2 Migration:**
- **Scope**: Comprehensive review of all BaseModel subclasses
- **Fixes required**:
  1. Replace `class Config:` with `model_config = ConfigDict(...)` (4 files)
  2. Update test code to use keyword arguments: `LictItem(key=0, value="a")`
  3. Review all BaseModel subclasses for v2 compatibility
- **Files with v1 Config**:
  - `src/jcx/bin/cx_task.py:24`
  - `src/jcx/time/calendar_type.py:15`
  - `src/jcx/time/calendar_type.py:35`
  - `src/jcx/time/clock_time.py:21`

### Claude's Discretion

- Exact `.expect()` message wording for each unwrap location
- Order of fixing tests (can prioritize by file/module)
- Whether to add helper functions for common unwrap patterns

### Deferred Ideas (OUT OF SCOPE)

- **FIX-02 (Assert replacement)**: Removed from Phase 1 scope, keeping assert statements as-is
- **Async MQTT testing**: Could explore async patterns for MQTT in future, but integration test marker is sufficient for now

</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| FIX-01 | Replace 33 unsafe `.unwrap()` calls with safe patterns | rustshed library provides `unwrap_or()`, `unwrap_or_else()`, `@to_option`, `@result_shortcut` decorators; see Architecture Patterns section |
| FIX-03 | Fix MQTT subscriber test hang (blocks CI/CD) | Use `@pytest.mark.integration` with pytest config `addopts = -m "not integration"`; root cause is `loop_forever()` blocking |
| FIX-04 | Fix Pydantic migration test failures | Migrate `class Config:` to `model_config = ConfigDict(...)`; update tests to use keyword arguments |
</phase_requirements>

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| rustshed | (from pyproject.toml) | Rust-style Result/Option types | Already used throughout codebase for error handling |
| pydantic | (from pyproject.toml) | Data validation with BaseModel | All Record classes inherit from BaseModel |
| pytest | (dev dep) | Test framework | Standard Python testing, already configured |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| pydantic-extra-types | (from pyproject.toml) | Extended Pydantic types | For specialized field types |
| loguru | (from pyproject.toml) | Logging | Error reporting in expect messages |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| rustshed | returns | rustshed already integrated; migration cost exceeds benefit |
| `.expect()` | Custom error type | Keep simple for Phase 1; can enhance later |

## Architecture Patterns

### Recommended Error Handling Flow

```
Fallible Operation → Return Result[T, E] or Option[T] → Caller handles with match/unwrap_or
```

### Pattern 1: Return Result/Option to Caller (Preferred)

**What:** Function returns `Result[T, E]` or `Option[T]`, caller decides how to handle failure.

**When to use:** Core business logic, functions that can fail.

**Example:**
```python
from rustshed import Result, Ok, Err, Option, Some, Null

@result_shortcut
def load_config(path: StrPath) -> Result[Config, Exception]:
    """Load config, return Result for caller to handle."""
    data = load_txt(path).Q  # .Q unwraps or propagates error
    return Ok(parse_config(data))

# Caller handles:
result = load_config("config.json")
if result.is_ok():
    config = result.unwrap()
else:
    handle_error(result.unwrap_err())
```

### Pattern 2: unwrap_or with Default

**What:** Provide fallback value when operation fails.

**When to use:** UI display, logging, non-critical operations.

**Example:**
```python
from rustshed import Option, Some, Null

def get_display_name(user: User) -> str:
    return user.nickname.unwrap_or(user.username)
```

### Pattern 3: expect for Unrecoverable Errors

**What:** Panic with detailed message when failure is unrecoverable.

**When to use:** Missing required config, invariant violation, cannot continue.

**Example:**
```python
def get_required_env(key: str) -> str:
    return os.environ.get(key).expect(f"Required environment variable {key} not set")
```

### Pattern 4: @to_option Decorator

**What:** Wrap functions that return None to return Option[T].

**When to use:** Converting existing None-returning functions.

**Example:**
```python
from rustshed import to_option, Option, Some, Null

@to_option
def find_user(id: int) -> User | None:
    # Returns None if not found
    return db.query(User).filter(id=id).first()

# Result is Option[User]
user: Option[User] = find_user(1)
```

### Anti-Patterns to Avoid

- **Bare `.unwrap()` without context:** Crashes with generic message, impossible to debug
- **Swallowing errors with `unwrap_or(None)`:** Hides failures that should be logged
- **Using `.unwrap()` in library code:** Forces crash on library consumers

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Safe unwrap with default | `if x is not None: return x else: return default` | `x.unwrap_or(default)` | Clearer intent, matches rustshed pattern |
| Safe unwrap with computation | `if x is not None: return x else: return compute()` | `x.unwrap_or_else(lambda: compute())` | Lazy evaluation |
| Converting exceptions to Result | try/except with Ok/Err | `@result_shortcut` decorator | Cleaner code, consistent pattern |
| Converting None to Option | `return Some(x) if x else Null` | `@to_option` decorator | Automatic wrapping |

## Common Pitfalls

### Pitfall 1: Using .unwrap() in Tests Without Context

**What goes wrong:** Test fails with cryptic "called unwrap on None/Err" message.

**Why it happens:** Tests use `.unwrap()` for convenience but don't provide context.

**How to avoid:** In tests, use `.unwrap()` for setup (acceptable), but for assertions use explicit checks or `.expect("test context")`.

**Warning signs:** Test failure message doesn't explain what was being tested.

### Pitfall 2: Mixing Pydantic v1 and v2 Patterns

**What goes wrong:** Deprecation warnings, runtime errors with model config.

**Why it happens:** Pydantic v2 changed Config syntax, but some files weren't updated.

**How to avoid:** Use `model_config = ConfigDict(...)` consistently. Search for `class Config:` in all BaseModel subclasses.

**Warning signs:** `PydanticDeprecatedSince20` warnings in test output.

### Pitfall 3: Blocking Tests with loop_forever()

**What goes wrong:** Test hangs indefinitely, CI/CD pipeline stalls.

**Why it happens:** `client.loop_forever()` in paho-mqtt blocks until disconnect.

**How to avoid:** Use `@pytest.mark.integration` for tests requiring external services. Configure pytest to skip by default.

**Warning signs:** Test runs longer than 30 seconds without output.

### Pitfall 4: Import Errors from Module Renames

**What goes wrong:** `ModuleNotFoundError` during test collection.

**Why it happens:** Module was renamed but imports weren't updated.

**How to avoid:** After any module rename, grep for old module name across all files including tests.

**Warning signs:** Pytest exits with collection errors before any tests run.

## Code Examples

### Pydantic v2 Migration

```python
# BEFORE (v1 style - deprecated)
from pydantic import BaseModel

class ClockPeriod(BaseModel):
    begin: ClockTime = ClockTime()
    end: ClockTime = ClockTime()

    class Config:
        frozen = True

# AFTER (v2 style)
from pydantic import BaseModel, ConfigDict

class ClockPeriod(BaseModel):
    model_config = ConfigDict(frozen=True)

    begin: ClockTime = ClockTime()
    end: ClockTime = ClockTime()
```

### Pytest Integration Test Marker

```python
# tests/net/subscriber_test.py
import pytest

@pytest.mark.integration
def test_mqtt_subscriber():
    """Integration test for MQTT - requires running broker."""
    cfg = MqttCfg("tcp://localhost:1883", "test_client")
    subscriber = Subscriber(cfg)
    # Test implementation
```

```toml
# pyproject.toml - pytest configuration
[tool.pytest.ini_options]
addopts = "-m 'not integration'"
markers = [
    "integration: marks tests as integration (deselect with '-m \"not integration\"')"
]
```

### Test Import Fix

```python
# BEFORE (broken import)
from jcx.api.task.task_db import TaskStatus, TaskInfo, TaskDb

# AFTER (correct import)
from jcx.api.task.task_types import TaskStatus, TaskInfo, TaskDb
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `class Config:` in Pydantic | `model_config = ConfigDict(...)` | Pydantic v2 (2023) | Deprecated warnings, future compatibility |
| Bare `.unwrap()` | Return Result/Option to caller | rustshed adoption | Safer error handling, explicit failure modes |
| Unit tests for external services | Integration test markers | pytest best practices | Faster test suites, clearer test categories |

**Deprecated/outdated:**
- Pydantic v1 `class Config:` syntax: Replaced by `model_config = ConfigDict(...)`

## Open Questions

1. **Should tests use `.unwrap()` or `.expect()`?**
   - What we know: Tests currently use `.unwrap()` extensively (50+ occurrences)
   - What's unclear: Whether to add `.expect()` messages for better test diagnostics
   - Recommendation: Keep `.unwrap()` in tests for now; focus on source code safety

2. **Should we add a project-wide conftest.py?**
   - What we know: No conftest.py exists in tests/ directory
   - What's unclear: Whether shared fixtures are needed
   - Recommendation: Add minimal conftest.py with integration marker registration

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest (from dev dependencies) |
| Config file | pyproject.toml `[tool.pytest.ini_options]` - needs creation |
| Quick run command | `pytest -x -q` |
| Full suite command | `pytest` |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| FIX-01 | Safe unwrap patterns | unit | `pytest -x -q` | Existing tests verify behavior |
| FIX-03 | MQTT test doesn't hang | integration | `pytest -m integration tests/net/` | `tests/net/subscriber_test.py` (needs marker) |
| FIX-04 | Pydantic v2 compatible | unit | `pytest tests/time/ tests/text/` | `tests/time/calendar_type_test.py`, `tests/text/txt_json_test.py` |

### Sampling Rate
- **Per task commit:** `pytest -x -q`
- **Per wave merge:** `pytest`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `pyproject.toml` - Add `[tool.pytest.ini_options]` with integration marker config
- [ ] `tests/conftest.py` - Register pytest markers (optional but recommended)
- [ ] Fix import errors in `tests/api/task/task_test.py` and `tests/api/task/test_task_db.py` (change `task_db` to `task_types`)

## Sources

### Primary (HIGH confidence)
- rustshed library - Already integrated in codebase, patterns verified in `src/jcx/text/txt_json.py`, `src/jcx/util/err.py`
- Pydantic v2 docs - ConfigDict migration pattern verified
- pytest docs - Integration marker pattern verified

### Secondary (MEDIUM confidence)
- Project source code analysis - Grep results for `.unwrap()`, `class Config:` patterns
- Test file inspection - Identified import errors and MQTT hang cause

### Tertiary (LOW confidence)
- None - All findings verified against source code or documentation

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - rustshed and pydantic already in use, patterns well-established
- Architecture: HIGH - Codebase analysis complete, patterns identified in existing code
- Pitfalls: HIGH - Root causes verified through source inspection and test runs

**Research date:** 2026-03-21
**Valid until:** 30 days - stable patterns, no breaking changes expected

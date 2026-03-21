# Phase 1: Foundation Repair - Context

**Gathered:** 2026-03-21
**Status:** Ready for planning

<domain>
## Phase Boundary

Eliminate crash risks from unsafe unwrap/assert patterns and repair broken tests. No new features - only ensure code is safe and tests pass reliably.

**Scope includes:**
- FIX-01: Replace 33 unsafe `.unwrap()` calls with safe patterns
- FIX-03: Fix MQTT subscriber test hang (blocks CI/CD)
- FIX-04: Fix Pydantic migration test failures

**Scope excludes:**
- FIX-02: Assert replacement (deferred - keeping assert statements as-is)

</domain>

<decisions>
## Implementation Decisions

### Unwrap Replacement Strategy

- **Primary approach**: Modify function signatures to return `Result[T, E]` or `Option[T]`, letting callers handle errors
- **When signature cannot change**: Preserve panic behavior but add detailed error messages using `.expect("detailed message")`
- **Signature changes**: Allowed - no backward compatibility requirement, follow rustshed style
- **Pattern selection by context**:
  - Core business logic → Return Result/Option
  - UI display/logging → `unwrap_or(default)` with silent fallback
  - Unrecoverable errors → `.expect()` with clear message

### Assert Replacement Strategy

- **Decision**: Skip assert replacement in Phase 1
- **Rationale**: Asserts are working as intended; reduces scope; can be addressed later if needed
- **Impact**: FIX-02 removed from Phase 1 scope

### MQTT Test Fix

- **Approach**: Mark as integration test, skip by default
- **Implementation**:
  - Add `@pytest.mark.integration` decorator to `tests/net/subscriber_test.py`
  - Configure pytest to skip integration tests by default
  - Run with `pytest -m integration` when needed
- **Root cause**: `dispatch_msg()` uses `loop_forever()` which blocks indefinitely

### Pydantic v2 Migration

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

</decisions>

<specifics>
## Specific Ideas

- "全面迁移到 Pydantic v2" - ensure all models are v2-compatible, not just fixing failing tests
- Rustshed library already provides safe alternatives: `unwrap_or()`, `unwrap_or_else()`, `match` patterns
- Existing error handling pattern: `@to_option`, `Ok/Err`, `Some/Null`

</specifics>

<code_context>
## Existing Code Insights

### Reusable Assets
- **rustshed library**: Already imported throughout codebase, provides `Result`, `Option`, `unwrap_or()`, `unwrap_or_else()`
- **`@to_option` decorator**: Wraps functions to return Option types automatically
- **`@result_shortcut` decorator**: Available for Result type wrapping
- **`src/jcx/util/err.py`**: Provides `show_err()` and `catch_show_err()` helpers

### Established Patterns
- Error handling: `Result[T, E]` for fallible operations, `Option[T]` for nullable returns
- Pydantic models: All Record classes inherit from `BaseModel`
- Test structure: `tests/` mirrors `src/` structure

### Integration Points
- 33 `.unwrap()` calls in 24 files (src/ and tests/)
- 7 failing tests related to Pydantic v2 migration
- 2 task test files with broken imports (task_db → task_types)
- MQTT test at `tests/net/subscriber_test.py:13`

</code_context>

<deferred>
## Deferred Ideas

- **FIX-02 (Assert replacement)**: Removed from Phase 1 scope, keeping assert statements as-is
- **Async MQTT testing**: Could explore async patterns for MQTT in future, but integration test marker is sufficient for now

</deferred>

---

*Phase: 01-foundation-repair*
*Context gathered: 2026-03-21*

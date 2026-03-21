---
phase: 01-foundation-repair
plan: 03
subsystem: error-handling
tags: [rustshed, Result, Option, unwrap, expect, error-propagation]

# Dependency graph
requires:
  - phase: 01-01
    provides: Test infrastructure and pytest configuration
  - phase: 01-02
    provides: Pydantic v2 migration for clean ConfigDict usage
provides:
  - Safe error handling patterns in library code
  - Result/Option return types for error propagation
  - expect() usage for clear error messages
affects: [02-security, all library modules]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Result[T, E] return type for fallible operations"
    - "Option[T] for nullable values with unwrap_or/expect"
    - "is_err() guard before unwrap() for safe access"
    - "expect() with descriptive message instead of bare unwrap()"

key-files:
  created: []
  modified:
    - src/jcx/api/_dao_list.py
    - src/jcx/api/task/task_client.py
    - src/jcx/db/rdb/db.py
    - src/jcx/db/jdb/util.py
    - src/jcx/db/jdb/variant.py
    - src/jcx/db/jdb/table.py
    - src/jcx/text/io.py
    - src/jcx/rs/rs.py
    - src/jcx/m/trace.py

key-decisions:
  - "Replace bare .unwrap() with .expect() for clear error messages when error already checked"
  - "Change replace_in_file signature to return Result[bool, str] for proper error propagation"
  - "Return default value on JSON parse error in RedisDb.get()"
  - "Skip files that fail to load with warning in load_list()"

patterns-established:
  - "Pattern: is_err() check followed by unwrap() is safe - add expect() for clarity"
  - "Pattern: Return Result type to caller for error propagation"
  - "Pattern: Use expect() with descriptive message for unrecoverable errors"

requirements-completed: [FIX-01]

# Metrics
duration: 3min
completed: 2026-03-21
---

# Phase 1 Plan 3: Safe Unwrap Replacement Summary

**Replaced unsafe `.unwrap()` calls in library code with safe patterns using Result/Option types from rustshed**

## Performance

- **Duration:** 3 min
- **Started:** 2026-03-21T13:54:02Z
- **Completed:** 2026-03-21T13:57:16Z
- **Tasks:** 3
- **Files modified:** 9

## Accomplishments

- Eliminated crash risks in API client layer by handling Null returns gracefully
- Added proper error propagation in text I/O with Result return type
- Replaced bare unwraps with expect() for clear error messages when guards exist
- Added warning logging for files that fail to load in database utilities

## Task Commits

Each task was committed atomically:

1. **Task 1: Replace unwraps in API client layer** - `c472c26` (fix)
2. **Task 2: Replace unwraps in DB layer** - `d8b26e2` (fix)
3. **Task 3: Replace unwraps in Text/Utility layer** - `230a883` (fix)

**Plan metadata:** (to be committed)

## Files Created/Modified

- `src/jcx/api/_dao_list.py` - Handle Null return from put() gracefully in update()
- `src/jcx/api/task/task_client.py` - Replace .unwrap() with .expect() after is_err() checks
- `src/jcx/db/rdb/db.py` - Return default value on JSON parse error
- `src/jcx/db/jdb/util.py` - Skip files that fail to load with warning
- `src/jcx/db/jdb/variant.py` - Use expect() for clear error message
- `src/jcx/db/jdb/table.py` - Use expect() for folder access
- `src/jcx/text/io.py` - Change replace_in_file to return Result[bool, str]
- `src/jcx/rs/rs.py` - Use expect() in py_optional conversion
- `src/jcx/m/trace.py` - Handle error case in trace_arr

## Decisions Made

- Used `.expect()` with descriptive messages instead of bare `.unwrap()` when error is already checked via `is_err()` - provides better debugging context
- Changed `replace_in_file()` signature from `-> None` to `-> Result[bool, str]` to propagate file load errors to callers
- In `load_list()`, files that fail to parse are skipped with a warning rather than crashing - maintains partial functionality

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

- Pre-existing test failure in `test_dao_list_client.py` unrelated to changes (test expects `json` key but code uses `data` key) - out of scope for this plan
- Some modules (cattr, torch) not installed in venv, but core modified modules import successfully

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- All library code now uses safe error handling patterns
- Ready for security and robustness improvements in Phase 2
- Remaining work: ensure all new code follows established patterns

## Self-Check: PASSED

- All 9 modified files verified to exist
- All 3 task commits verified in git history

---
*Phase: 01-foundation-repair*
*Completed: 2026-03-21*

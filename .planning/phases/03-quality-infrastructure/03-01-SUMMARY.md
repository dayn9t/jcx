---
phase: 03-quality-infrastructure
plan: 01
subsystem: testing
tags: [ruff, linting, formatting, pytest-cov, coverage, quality-tools]

# Dependency graph
requires: []
provides:
  - Unified Ruff configuration for linting and formatting
  - Coverage enforcement with 80% threshold
affects: [03-02, 03-03, 03-04, 03-05]

# Tech tracking
tech-stack:
  added: [pytest-cov, coverage[toml]]
  patterns: [coverage-fail-under-enforcement, ruff-unified-lint-format]

key-files:
  created: []
  modified:
    - ruff.toml
    - pyproject.toml

key-decisions:
  - "Use Ruff for both linting and formatting with select=['ALL']"
  - "Enforce 80% coverage threshold with fail_under"

patterns-established:
  - "Coverage configuration with branch coverage and exclusion patterns"

requirements-completed: [QLTY-03, QLTY-01]

# Metrics
duration: 1min
completed: 2026-03-22
---

# Phase 3 Plan 01: Quality Tools Configuration Summary

**Configured Ruff for unified linting and formatting, and pytest-cov for coverage enforcement with 80% threshold**

## Performance

- **Duration:** 1 min
- **Started:** 2026-03-22T03:37:53Z
- **Completed:** 2026-03-22T03:38:53Z
- **Tasks:** 2
- **Files modified:** 2

## Accomplishments

- Extended ruff.toml with format configuration and per-file-ignores for tests
- Added pytest-cov and coverage[toml] dependencies
- Configured coverage with fail_under=80 enforcement, branch coverage, and exclusion patterns

## Task Commits

Each task was committed atomically:

1. **Task 1: Configure Ruff for linting and formatting** - `af3259a` (feat)
2. **Task 2: Add pytest-cov dependency and configure coverage** - `20eb04b` (feat)

## Files Created/Modified

- `ruff.toml` - Extended with target-version, line-length, per-file-ignores, and [format] section
- `pyproject.toml` - Added pytest-cov deps, coverage addopts, [tool.coverage.run], [tool.coverage.report]

## Decisions Made

- Kept existing `select = ["ALL"]` for linting as project already uses comprehensive rule set
- Added S101 (assert) to per-file-ignores for tests to allow assertions in test files
- Set fail_under=80 as enforcement threshold (current coverage ~34%, will need to improve)

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

- Current test coverage is 34%, below the 80% threshold. This is expected - the fail_under provides enforcement mechanism for future improvement.
- Pre-existing test failures in test_counter, test_publish, test_is_this_week, test_lict_1, test_lict_2 were observed but are out of scope.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Ruff configuration ready for CI/CD integration
- Coverage enforcement configured; may need to temporarily lower threshold if baseline coverage blocks development
- Pre-commit hooks (plan 03-02) can now consume these configurations

---
*Phase: 03-quality-infrastructure*
*Completed: 2026-03-22*

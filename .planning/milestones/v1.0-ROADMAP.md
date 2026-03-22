# Roadmap: jcx Library Refactoring

## Overview

Refactoring the jcx Python utility library to eliminate crash risks, improve error handling, establish CI/CD quality gates, and complete documentation. The journey takes the codebase from 33 unsafe unwrap calls and broken tests to a production-ready library with 80% coverage, proper type safety, and comprehensive documentation.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [x] **Phase 1: Foundation Repair** - Eliminate crash risks from unsafe unwrap patterns and repair broken tests
- [x] **Phase 2: Security & Robustness** - Add timeouts, narrow exception handling, complete incomplete implementations
- [x] **Phase 3: Quality Infrastructure** - Establish CI/CD, coverage reporting, linting, and structured logging
- [ ] **Phase 4: Type Safety & Documentation** - Fix type:ignore issues, add stubs, complete documentation

## Phase Details

### Phase 1: Foundation Repair
**Goal**: Tests pass reliably and code has no crash risks from unsafe patterns
**Depends on**: Nothing (first phase)
**Requirements**: FIX-01, FIX-03, FIX-04
**Success Criteria** (what must be TRUE):
  1. All 33 unsafe `.unwrap()` calls replaced with safe patterns (`.expect()`, `unwrap_or()`, or Result returns)
  2. MQTT subscriber test no longer hangs (marked as integration test, skipped by default)
  3. Pydantic migration test failures resolved (all tests pass)
**Plans**: 4 plans in 2 waves

Plans:
- [x] 01-01: Test infrastructure setup (pytest config, import fixes, MQTT marker)
- [x] 01-02: Pydantic v2 migration (ConfigDict for all BaseModel subclasses)
- [x] 01-03: Unwrap replacement in library code (API, DB, Text layers)
- [x] 01-04: Unwrap replacement in CLI tools (cx_task, cx_dao, cx_hisotry_clean)

**Note**: FIX-02 (assert replacement) is deferred. Asserts are working as intended and can be addressed in a future phase if needed.

### Phase 2: Security & Robustness
**Goal**: HTTP connections have timeouts, exceptions are specific, incomplete implementations are finished
**Depends on**: Phase 1
**Requirements**: FIX-05, FIX-06, SEC-01, SEC-02, SEC-03, SEC-04
**Success Criteria** (what must be TRUE):
  1. HTTP connections in dao_client.py have configurable timeouts and pool limits
  2. All broad `except Exception` catches replaced with specific exception types (10 locations)
  3. CLI tools validate input using Pydantic models before processing
  4. Redis URL handling uses Result/Option types instead of assert
  5. Calendar weekday checking completed in CalendarTrigger.check()
  6. File time utility implements Iterator pattern as designed
**Plans**: 6 plans in 2 waves

Plans:
- [x] 02-01: HTTP timeouts, pool limits, and specific exceptions in DaoListClient (SEC-01, SEC-02)
- [x] 02-02: Redis URL Result-based parsing (SEC-04)
- [x] 02-03: Calendar weekday checking in CalendarTrigger (FIX-05)
- [x] 02-04: FileTimeIterator implementation (FIX-06)
- [x] 02-05: Specific exception handling in text utilities (SEC-02)
- [x] 02-06: CLI input validation and exception handling (SEC-02, SEC-03)

### Phase 3: Quality Infrastructure
**Goal**: Automated quality gates enforce 80% coverage, consistent formatting, and logging standards
**Depends on**: Phase 2
**Requirements**: QLTY-01, QLTY-02, QLTY-03, QLTY-04, QLTY-05, SEC-05
**Success Criteria** (what must be TRUE):
  1. pytest-cov reports coverage with 80% threshold enforced in CI
  2. GitHub Actions CI/CD pipeline runs on every push and PR
  3. Ruff replaces black, isort, flake8 for unified linting and formatting
  4. Pre-commit hooks enforce quality gates before commits land
  5. Structured logging configuration available across all modules
  6. Secret management documented with .env.example and required env vars list
**Plans**: 5 plans in 3 waves

Plans:
- [x] 03-01: Ruff and coverage configuration (QLTY-03, QLTY-01)
- [x] 03-02: GitHub Actions CI/CD pipeline (QLTY-02)
- [x] 03-03: Pre-commit hooks with ruff (QLTY-04)
- [x] 03-04: Structured logging configuration (QLTY-05)
- [x] 03-05: Secret management documentation (SEC-05)

### Phase 4: Type Safety & Documentation
**Goal**: All type:ignore comments resolved, public APIs documented with examples
**Depends on**: Phase 3
**Requirements**: TYPE-01, TYPE-02, TYPE-03, DOC-01, DOC-02, DOC-03
**Success Criteria** (what must be TRUE):
  1. All 9 `# type: ignore` comments reviewed and either fixed or documented as necessary
  2. Type stubs added for paho-mqtt or documented why ignore is necessary
  3. All public APIs have type hints verified by pyright
  4. README updated with usage examples for each major module
  5. All public functions have docstrings with parameter descriptions
  6. Required environment variables documented in README and .env.example
**Plans**: 5 plans in 3 waves

Plans:
- [x] 04-01-PLAN.md: Type ignore cleanup and pyright setup (TYPE-01, TYPE-02)
- [x] 04-02-PLAN.md: Type hint verification for public APIs (TYPE-03)
- [x] 04-03-PLAN.md: README documentation update (DOC-01, DOC-03)
- [x] 04-04-PLAN.md: Docstrings for public functions (DOC-02)
- [ ] 04-05-PLAN.md: Gap closure - fix verification failures (TYPE-01, TYPE-03, DOC-01)

## Progress

**Execution Order:**
Phases execute in numeric order: 1 -> 2 -> 3 -> 4

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Foundation Repair | 4/4 | Complete | 01-01, 01-02, 01-03, 01-04 |
| 2. Security & Robustness | 6/6 | Complete | 02-01, 02-02, 02-03, 02-04, 02-05, 02-06 |
| 3. Quality Infrastructure | 5/5 | Complete | 03-01, 03-02, 03-03, 03-04, 03-05 |
| 4. Type Safety & Documentation | 4/5 | In progress | 04-01, 04-02, 04-03, 04-04 |

---
*Roadmap created: 2026-03-21*
*Last updated: 2026-03-22 - Phase 4 Plans 1-4 complete, gap closure plan added*
*Granularity: coarse (4 phases)*

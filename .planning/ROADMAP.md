# Roadmap: jcx Library Refactoring

## Overview

Refactoring the jcx Python utility library to eliminate crash risks, improve error handling, establish CI/CD quality gates, and complete documentation. The journey takes the codebase from 33 unsafe unwrap calls and broken tests to a production-ready library with 80% coverage, proper type safety, and comprehensive documentation.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [ ] **Phase 1: Foundation Repair** - Eliminate crash risks from unsafe unwrap/assert patterns and repair broken tests
- [ ] **Phase 2: Security & Robustness** - Add timeouts, narrow exception handling, complete incomplete implementations
- [ ] **Phase 3: Quality Infrastructure** - Establish CI/CD, coverage reporting, linting, and structured logging
- [ ] **Phase 4: Type Safety & Documentation** - Fix type:ignore issues, add stubs, complete documentation

## Phase Details

### Phase 1: Foundation Repair
**Goal**: Tests pass reliably and code has no crash risks from unsafe patterns
**Depends on**: Nothing (first phase)
**Requirements**: FIX-01, FIX-02, FIX-03, FIX-04
**Success Criteria** (what must be TRUE):
  1. All 33 unsafe `.unwrap()` calls replaced with safe patterns (`unwrap_or()`, `unwrap_or_else()`, or match)
  2. All 23 production `assert` statements replaced with proper validation (if/raise or Result types)
  3. MQTT subscriber test no longer hangs (CI/CD can run without blocking)
  4. Pydantic migration test failures resolved (all tests pass)
**Plans**: TBD

Plans:
- [ ] 01-01: Replace unsafe unwrap patterns
- [ ] 01-02: Replace production assert statements
- [ ] 01-03: Fix broken tests (MQTT hang, Pydantic failures)

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
**Plans**: TBD

Plans:
- [ ] 02-01: Add HTTP timeouts and pool limits
- [ ] 02-02: Narrow exception handling to specific types
- [ ] 02-03: Complete incomplete implementations (calendar, file utility)
- [ ] 02-04: Add CLI input validation

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
**Plans**: TBD

Plans:
- [ ] 03-01: Configure pytest-cov with 80% threshold
- [ ] 03-02: Establish GitHub Actions CI/CD pipeline
- [ ] 03-03: Configure Ruff for linting and formatting
- [ ] 03-04: Add pre-commit hooks
- [ ] 03-05: Implement structured logging and secret docs

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
**Plans**: TBD

Plans:
- [ ] 04-01: Fix or document all type:ignore comments
- [ ] 04-02: Verify type hints on all public APIs
- [ ] 04-03: Update README with usage examples
- [ ] 04-04: Add docstrings to all public functions

## Progress

**Execution Order:**
Phases execute in numeric order: 1 -> 2 -> 3 -> 4

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Foundation Repair | 0/3 | Not started | - |
| 2. Security & Robustness | 0/4 | Not started | - |
| 3. Quality Infrastructure | 0/5 | Not started | - |
| 4. Type Safety & Documentation | 0/4 | Not started | - |

---
*Roadmap created: 2026-03-21*
*Granularity: coarse (4 phases)*

# Project Research Summary

**Project:** jcx - Python Utility Library Refactoring
**Domain:** Python utility library quality improvement with Rust-style type safety
**Researched:** 2026-03-21
**Confidence:** HIGH

## Executive Summary

jcx is a Python utility library providing CLI tools, HTTP API clients, database abstractions (JSON file-based and Redis), MQTT networking, and time utilities. The library adopts Rust-style error handling via the rustshed library (Option/Result types) but currently has 33 unsafe `.unwrap()` calls and 23 assert statements that create crash risks in production.

The recommended approach is a phased refactoring focused on eliminating crash risks first, then improving error handling patterns, and finally establishing CI/CD quality gates. Key risks include: (1) unsafe unwrapping causing runtime panics, (2) assert statements skipped in optimized Python mode, and (3) broad exception handling hiding bugs. All research sources agree on the same priorities - fix unsafe patterns before adding new features.

## Key Findings

### Recommended Stack

The research strongly recommends consolidating quality tooling around Ruff (replacing black, isort, flake8, pyupgrade) and adding pytest-cov for coverage enforcement. Pyright is preferred over mypy for faster type checking (3-5x speed advantage in CI/CD). The `returns` library is recommended for new code over rustshed due to better Python idioms and active maintenance, but migration should be gradual.

**Core technologies:**
- **Ruff 0.14.3+:** All-in-one linter and formatter - replaces 20+ tools, 10-100x faster, written in Rust
- **pytest-cov 7.0.0+:** Coverage reporting - currently missing, required for 80% coverage threshold
- **Pyright 1.1.390+:** Type checker - 3-5x faster than mypy, better modern Python inference
- **pre-commit 4.0+:** Git hooks framework - enforces quality gates before commits

**Supporting libraries:**
- **returns 0.24.0+:** Functional error handling - gradual replacement for rustshed in new code
- **pytest-mock 3.14+:** Mocking utilities - cleaner test patterns for 64 existing mock references

### Expected Features

**Must have (table stakes):**
- Type hints on all public APIs - foundation for static analysis and IDE support
- 80%+ test coverage - confidence that refactoring did not break functionality
- Specific exception handling - replace broad `except Exception` with targeted catches
- CI/CD pipeline - automated testing on every change
- Pinned dependencies - reproducible builds
- README with usage examples - user onboarding

**Should have (competitive):**
- Rust-style Option/Result types - already using rustshed, maintain consistency
- Pre-commit hooks - consistent code quality before commits
- Comprehensive type checking (strict mode) - catch bugs at development time
- Dependency vulnerability scanning - supply chain security

**Defer (v2+):**
- Async/await support - requires significant API changes, not needed now
- 100% test coverage - diminishing returns, 80% is sufficient
- Multiple serialization formats - JSON is adequate for current needs
- FastAPI migration - Flask-RESTX replacement exceeds minimum scope

### Architecture Approach

The codebase follows a layered architecture with CLI at the top, API/Networking in the middle, Data Access below, and Utilities at the bottom. The key pattern is Rust-style Result/Option for fallible operations. The current structure is sound but has unsafe unwrapping throughout.

**Major components:**
1. **CLI Layer (bin/)** - Command-line entry points using typer/rich
2. **API Layer (api/)** - HTTP clients with requests.Session, Result-wrapped responses
3. **Data Access Layer (db/)** - jdb (JSON files) and rdb (Redis) with Pydantic models
4. **Utilities Layer (util/, sys/, text/, m/)** - Core functions, file ops, JSON I/O, math

### Critical Pitfalls

1. **Unsafe `.unwrap()` calls (33 instances)** - Replace with `unwrap_or()`, `unwrap_or_else()`, or explicit error handling before any other work
2. **Assert statements in production (23 instances)** - Replace with proper validation using if/raise or Result types; assert is skipped with `-O` flag
3. **Broad `except Exception` handling** - Narrow to specific exception types; never catch without re-raising
4. **MQTT subscriber test hang** - Fix blocking test before CI/CD can be reliable
5. **Type ignore comments (9 instances)** - Add proper type stubs or document why ignore is needed

## Implications for Roadmap

Based on research, suggested phase structure:

### Phase 1: Foundation - Test Repair & Critical Fixes
**Rationale:** Cannot safely refactor without working tests. 33 unsafe unwrap calls create crash risk that must be eliminated before any other changes.
**Delivers:** Working test suite, no crash risks from unwrap/assert
**Addresses:** Type hints on public APIs, specific exception handling
**Avoids:** Pydantic migration test failures, unwrap panics, assert validation bypass

### Phase 2: Error Handling Improvements
**Rationale:** With tests passing, systematically improve error handling patterns. Narrow exception catches, add timeouts to HTTP requests.
**Delivers:** Robust error handling, no hidden bugs
**Uses:** rustshed/returns Result types, specific exception types
**Implements:** Safe unwrapping patterns, explicit validation replacing assert

### Phase 3: Quality Infrastructure
**Rationale:** Establish CI/CD pipeline and coverage enforcement. Only after code is stable can quality gates be meaningful.
**Delivers:** Automated quality enforcement, coverage visibility
**Uses:** pytest-cov, pre-commit, Ruff, Pyright
**Implements:** 80% coverage threshold, linting on every commit

### Phase 4: Tech Debt Cleanup
**Rationale:** Address incomplete implementations and type ignore comments. Lower priority than crash prevention.
**Delivers:** Clean codebase, no TODO dead-ends
**Addresses:** Calendar weekday checking, file time utility, type stubs for paho-mqtt

### Phase 5: Documentation & Finalization
**Rationale:** Documentation should reflect final API, not intermediate states.
**Delivers:** README, usage examples, API documentation
**Addresses:** README with usage examples, API reference generation

### Phase Ordering Rationale

- **Phase 1 first:** Tests must pass before any refactoring. Unsafe patterns create production crash risk.
- **Phase 2 second:** Error handling improvements build on stable test foundation.
- **Phase 3 third:** CI/CD only meaningful after code quality is improved.
- **Phase 4 fourth:** Tech debt cleanup requires stable foundation.
- **Phase 5 last:** Documentation reflects final state, not intermediate.

### Research Flags

Phases likely needing deeper research during planning:
- **Phase 4:** Dynamic API model generation - Flask-RESTX patterns need investigation for potential FastAPI migration path

Phases with standard patterns (skip research-phase):
- **Phase 1:** Well-documented patterns for unwrap/assert replacement
- **Phase 2:** Standard Python exception handling best practices
- **Phase 3:** Standard pytest-cov and pre-commit configurations

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | PyPI versions verified, Astral (Ruff creators) is reputable, returns library actively maintained |
| Features | HIGH | Industry standard table stakes, Real Python and official pytest docs consulted |
| Architecture | HIGH | Direct codebase analysis combined with official Python packaging patterns |
| Pitfalls | HIGH | Official Pydantic docs, Rust documentation for Option/Result, multiple community sources agree |

**Overall confidence:** HIGH

### Gaps to Address

- **rustshed vs returns migration path:** Research suggests returns for new code, but exact migration strategy for existing 55+ Result/Option uses needs planning decision
- **Flask-RESTX to FastAPI migration:** Flagged as out of scope but may need future research if API layer is significantly modified
- **Arrow dependency:** Tests reference arrow but migration path to datetime/pendulum unclear - needs decision during tech debt phase

## Sources

### Primary (HIGH confidence)
- PyPI Ruff (pypi.org/project/ruff/) - version 0.14.3, official package registry
- PyPI pytest-cov (pypi.org/project/pytest-cov/) - version 7.0.0, official package registry
- Pydantic Migration Guide (docs.pydantic.dev/latest/migration/) - official documentation
- pytest Good Integration Practices (docs.pytest.org/en/stable/explanation/goodpractices.html) - official docs
- Python Packaging Authority GitHub Actions guide - official packaging guide

### Secondary (MEDIUM confidence)
- dry-python/returns GitHub - active maintenance, version 0.24.0
- Pyright vs Mypy benchmarks - community benchmarks show 3-5x speed advantage
- Real Python Code Quality Guide (realpython.com/python-code-quality/) - established community resource
- dbader.org Python Refactoring Gone Wrong - experienced practitioner guidance

### Tertiary (Codebase Analysis)
- .planning/codebase/ARCHITECTURE.md - direct analysis of existing structure
- .planning/codebase/CONCERNS.md - identified 33 unwrap, 23 assert, 9 type: ignore issues

---
*Research completed: 2026-03-21*
*Ready for roadmap: yes*

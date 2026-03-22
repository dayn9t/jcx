# Requirements: jcx Library Refactoring

**Defined:** 2026-03-21
**Core Value:** Quality first - unified API style, improved error handling, code correctness

## v1 Requirements

Requirements for refactoring completion. Each maps to roadmap phases.

### Critical Fixes

- [x] **FIX-01**: Replace all 33 unsafe `.unwrap()` calls with safe patterns (`unwrap_or()`, `unwrap_or_else()`, or match)
- [ ] **FIX-02**: Replace all 23 production `assert` statements with proper validation (if/raise or Result types)
- [ ] **FIX-03**: Fix MQTT subscriber test hang (currently blocks CI/CD)
- [x] **FIX-04**: Fix Pydantic migration test failures
- [x] **FIX-05**: Complete calendar weekday checking in `CalendarTrigger.check()`
- [x] **FIX-06**: Implement file time utility using Iterator pattern

### Security

- [ ] **SEC-01**: Add HTTP connection timeouts and pool limits to `dao_client.py`
- [ ] **SEC-02**: Replace broad `except Exception` with specific exception types (10 locations)
- [ ] **SEC-03**: Add input validation to CLI tools using Pydantic models
- [x] **SEC-04**: Replace Redis URL assert with proper Result/Option error handling
- [x] **SEC-05**: Add secret management documentation (`.env.example`, required env vars)

### Quality Infrastructure

- [x] **QLTY-01**: Add pytest-cov for coverage reporting with 80% threshold
- [x] **QLTY-02**: Establish CI/CD pipeline (GitHub Actions recommended)
- [x] **QLTY-03**: Configure Ruff for linting and formatting (replace black, isort, flake8)
- [x] **QLTY-04**: Add pre-commit hooks for quality gates
- [ ] **QLTY-05**: Implement structured logging configuration

### Type Safety

- [ ] **TYPE-01**: Review and fix all 9 `# type: ignore` comments
- [ ] **TYPE-02**: Add type stubs for paho-mqtt or document why ignore is necessary
- [ ] **TYPE-03**: Verify all public APIs have type hints

### Documentation

- [ ] **DOC-01**: Update README with usage examples
- [ ] **DOC-02**: Add docstrings to all public functions
- [ ] **DOC-03**: Document required environment variables

## v2 Requirements

Deferred to future release. Tracked but not in current roadmap.

### Architecture Improvements

- **ARCH-01**: Migrate Flask-RESTX to FastAPI for automatic model generation
- **ARCH-02**: Consider rustshed to returns migration for new code
- **ARCH-03**: Add async/await support for file I/O and HTTP

### Extended Quality

- **QLTY-06**: Dependency vulnerability scanning (Safety/Dependabot)
- **QLTY-07**: Automated releases with python-semantic-release
- **QLTY-08**: API documentation generation (MkDocs + mkdocstrings)
- **QLTY-09**: Retry logic with exponential backoff

## Out of Scope

Explicitly excluded. Documented to prevent scope creep.

| Feature | Reason |
|---------|--------|
| Async/await everywhere | Requires significant API changes; sync API sufficient for current needs |
| 100% test coverage | Diminishing returns; 80% is sufficient for refactoring confidence |
| FastAPI migration | Exceeds minimum scope; Flask-RESTX functional for now |
| Multiple serialization formats | JSON is adequate for current needs |
| Performance optimization beyond fixes | Not identified as blocking issue |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| FIX-01 | Phase 1: Foundation Repair | Complete |
| FIX-02 | Phase 1: Foundation Repair | Pending |
| FIX-03 | Phase 1: Foundation Repair | Pending |
| FIX-04 | Phase 1: Foundation Repair | Complete |
| FIX-05 | Phase 2: Security & Robustness | Complete |
| FIX-06 | Phase 2: Security & Robustness | Complete |
| SEC-01 | Phase 2: Security & Robustness | Pending |
| SEC-02 | Phase 2: Security & Robustness | Pending |
| SEC-03 | Phase 2: Security & Robustness | Pending |
| SEC-04 | Phase 2: Security & Robustness | Complete |
| SEC-05 | Phase 3: Quality Infrastructure | Complete |
| QLTY-01 | Phase 3: Quality Infrastructure | Complete |
| QLTY-02 | Phase 3: Quality Infrastructure | Complete |
| QLTY-03 | Phase 3: Quality Infrastructure | Complete |
| QLTY-04 | Phase 3: Quality Infrastructure | Complete |
| QLTY-05 | Phase 3: Quality Infrastructure | Pending |
| TYPE-01 | Phase 4: Type Safety & Documentation | Pending |
| TYPE-02 | Phase 4: Type Safety & Documentation | Pending |
| TYPE-03 | Phase 4: Type Safety & Documentation | Pending |
| DOC-01 | Phase 4: Type Safety & Documentation | Pending |
| DOC-02 | Phase 4: Type Safety & Documentation | Pending |
| DOC-03 | Phase 4: Type Safety & Documentation | Pending |

**Coverage:**
- v1 requirements: 21 total
- Mapped to phases: 21
- Unmapped: 0

---
*Requirements defined: 2026-03-21*
*Last updated: 2026-03-22 - FIX-05 completed*

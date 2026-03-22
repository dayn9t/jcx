---
phase: 2
slug: security-robustness
status: complete
nyquist_compliant: true
wave_0_complete: true
created: 2026-03-21
updated: 2026-03-23
---

# Phase 2 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest |
| **Config file** | `pyproject.toml` ([tool.pytest.ini_options]) |
| **Quick run command** | `pytest tests/ -x -v --ignore=tests/net/subscriber_test.py` |
| **Full suite command** | `pytest tests/ -v` |
| **Estimated runtime** | ~30 seconds |

---

## Sampling Rate

- **After every task commit:** Run `pytest tests/ -x --ignore=tests/net/subscriber_test.py`
- **After every plan wave:** Run `pytest tests/ -v`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 30 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 02-01-01 | 01 | 1 | SEC-01 | unit | `pytest tests/api/test_dao_list_client.py -v` | ✅ | ⬜ pending |
| 02-01-02 | 01 | 1 | SEC-02 | unit | `pytest tests/api/test_dao_list_client.py -v` | ✅ | ⬜ pending |
| 02-02-01 | 02 | 1 | SEC-02 | unit | `pytest tests/ -k "exception" -v` | ❌ W0 | ⬜ pending |
| 02-03-01 | 03 | 1 | SEC-03 | integration | `pytest tests/ -k "cli" -v` | ❌ W0 | ⬜ pending |
| 02-04-01 | 04 | 1 | SEC-04 | unit | `pytest tests/db/ -v` | ❌ W0 | ⬜ pending |
| 02-05-01 | 05 | 2 | FIX-05 | unit | `pytest tests/time/calendar_type_test.py -v` | ❌ W0 | ⬜ pending |
| 02-06-01 | 06 | 2 | FIX-06 | unit | `pytest tests/sys/fs_test.py -v` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/time/calendar_type_test.py` — add weekday filtering tests
- [ ] `tests/sys/fs_test.py` — add FileTimeIterator tests
- [ ] `tests/db/rdb/db_test.py` — add Redis URL parsing tests (may need mock)
- [ ] `tests/api/test_cli_validation.py` — add CLI input validation tests

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| None | - | - | All phase behaviors have automated verification |

*All phase behaviors have automated verification.*

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 30s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending

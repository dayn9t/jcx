---
phase: 1
slug: foundation-repair
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-21
---

# Phase 1 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest (from dev dependencies) |
| **Config file** | pyproject.toml `[tool.pytest.ini_options]` - needs creation |
| **Quick run command** | `pytest -x -q` |
| **Full suite command** | `pytest` |
| **Estimated runtime** | ~30 seconds |

---

## Sampling Rate

- **After every task commit:** Run `pytest -x -q`
- **After every plan wave:** Run `pytest`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 30 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 01-01-01 | 01 | 1 | FIX-01 | unit | `pytest -x -q` | ✅ existing | ⬜ pending |
| 01-01-02 | 01 | 1 | FIX-01 | unit | `pytest -x -q` | ✅ existing | ⬜ pending |
| 01-02-01 | 02 | 1 | FIX-03 | integration | `pytest -m integration tests/net/` | ⚠️ needs marker | ⬜ pending |
| 01-03-01 | 03 | 2 | FIX-04 | unit | `pytest tests/time/ tests/text/` | ✅ existing | ⬜ pending |
| 01-03-02 | 03 | 2 | FIX-04 | unit | `pytest tests/time/ tests/text/` | ✅ existing | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `pyproject.toml` — Add `[tool.pytest.ini_options]` with integration marker config
- [ ] `tests/conftest.py` — Register pytest markers (optional but recommended)
- [ ] Fix import errors in `tests/api/task/task_test.py` and `tests/api/task/test_task_db.py` (change `task_db` to `task_types`)

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| MQTT integration test runs without hang | FIX-03 | Requires running MQTT broker | Run `pytest -m integration tests/net/subscriber_test.py` with local broker |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 30s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending

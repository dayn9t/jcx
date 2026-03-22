---
phase: 4
slug: type-safety-documentation
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-22
---

# Phase 4 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 8.x |
| **Config file** | pyproject.toml |
| **Quick run command** | `uv run pytest -x -q` |
| **Full suite command** | `uv run pytest --cov=src/jcx --cov-fail-under=80` |
| **Estimated runtime** | ~30 seconds |

---

## Sampling Rate

- **After every task commit:** Run `uv run pytest -x -q`
- **After every plan wave:** Run `uv run pytest --cov=src/jcx`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 30 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 04-01-01 | 01 | 1 | TYPE-01 | static | `uv run pyright src/jcx` | ✅ | ⬜ pending |
| 04-01-02 | 01 | 1 | TYPE-02 | static | `uv run pyright src/jcx` | ✅ | ⬜ pending |
| 04-02-01 | 02 | 1 | TYPE-03 | static | `uv run pyright --verifytypes jcx` | ✅ | ⬜ pending |
| 04-03-01 | 03 | 2 | DOC-01 | manual | Review README examples | ✅ | ⬜ pending |
| 04-03-02 | 03 | 2 | DOC-03 | manual | Review .env.example | ✅ | ⬜ pending |
| 04-04-01 | 04 | 2 | DOC-02 | static | `uv run pydocstyle src/jcx` | ⚠️ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `py.typed` marker file — PEP 561 compliance for type hints
- [ ] pydocstyle configuration in pyproject.toml (if used for docstring verification)

*Existing pytest infrastructure covers all test requirements.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| README examples are readable | DOC-01 | Human readability check | Review rendered README.md |
| Environment variable docs complete | DOC-03 | Documentation quality | Review .env.example comments |

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references
- [x] No watch-mode flags
- [x] Feedback latency < 30s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending

---
phase: 3
slug: quality-infrastructure
status: draft
nyquist_compliant: true
wave_0_complete: false
created: 2026-03-22
---

# Phase 3 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.0.1 |
| **Config file** | pyproject.toml [tool.pytest.ini_options] |
| **Quick run command** | `uv run pytest -m "not integration" -x` |
| **Full suite command** | `uv run pytest --cov=jcx --cov-fail-under=80` |
| **Estimated runtime** | ~30 seconds |

---

## Sampling Rate

- **After every task commit:** Run `uv run pytest -m "not integration" -x`
- **After every plan wave:** Run `uv run pytest --cov=jcx`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 30 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 03-01-01 | 01 | 1 | QLTY-01 | config | `uv run pytest --cov=jcx --cov-fail-under=80` | ❌ W0 | ⬜ pending |
| 03-02-01 | 02 | 2 | QLTY-02 | workflow | `gh workflow run ci.yml` | ❌ W0 | ⬜ pending |
| 03-03-01 | 03 | 1 | QLTY-03 | config | `uv run ruff check && uv run ruff format --check` | ❌ W0 | ⬜ pending |
| 03-04-01 | 04 | 2 | QLTY-04 | config | `pre-commit run --all-files` | ❌ W0 | ⬜ pending |
| 03-05-01 | 05 | 3 | QLTY-05 | unit | `uv run pytest tests/util/ -k logging` | ❌ W0 | ⬜ pending |
| 03-06-01 | 06 | 3 | SEC-05 | manual | N/A - documentation task | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/util/logging_config_test.py` — stubs for QLTY-05 structured logging
- [ ] `.github/workflows/ci.yml` — GitHub Actions workflow (Wave 0 creates skeleton)
- [ ] `.pre-commit-config.yaml` — Pre-commit hooks (Wave 0 creates skeleton)
- [ ] `.env.example` — Secret documentation template
- [ ] `pyproject.toml` — Add coverage and ruff config sections
- [ ] `.gitignore` — Add `.env` pattern

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| CI runs on PR | QLTY-02 | Requires GitHub PR workflow | Create test PR, verify CI triggers |
| Pre-commit blocks bad commit | QLTY-04 | Requires git hook execution | Make intentional lint error, verify hook blocks |
| .env.example documents all vars | SEC-05 | Documentation task | Review checklist completeness |

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references
- [x] No watch-mode flags
- [x] Feedback latency < 30s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** approved 2026-03-22

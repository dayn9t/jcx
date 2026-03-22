# Phase 3: Quality Infrastructure - Research

**Researched:** 2026-03-22
**Domain:** Python CI/CD, Testing, Linting, Logging, Secret Management
**Confidence:** HIGH

## Summary

This research covers the implementation of automated quality gates for the jcx Python library. The project currently has basic pytest setup (26 test files, 84 source files), uses `loguru` for logging (5 files), has minimal `ruff.toml` configuration, but lacks CI/CD, coverage enforcement, pre-commit hooks, and secret management documentation.

**Primary recommendation:** Use the Astral ecosystem (uv + ruff) for consistency and speed. Leverage existing loguru instead of adding structlog. Create GitHub Actions workflow with caching for fast CI.

## User Constraints (from CONTEXT.md)

No CONTEXT.md exists for this phase. Research proceeds without locked decisions.

## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| QLTY-01 | pytest-cov with 80% threshold | coverage.py with `fail_under` in pyproject.toml |
| QLTY-02 | GitHub Actions CI/CD pipeline | uv + pytest + ruff workflow with caching |
| QLTY-03 | Ruff for linting/formatting | Extend existing ruff.toml, add format config |
| QLTY-04 | Pre-commit hooks | ruff pre-commit hooks + coverage gate |
| QLTY-05 | Structured logging configuration | Configure loguru for JSON output (already in use) |
| SEC-05 | Secret management documentation | .env.example + required env vars list |

## Current Project State

### Existing Infrastructure

| Component | Status | Notes |
|-----------|--------|-------|
| pytest | Installed | v9.0.1, 26 test files, markers for integration tests |
| ruff.toml | Minimal | Only lint.select and lint.ignore configured |
| loguru | In use | 5 files use `from loguru import logger` |
| .gitignore | Present | Missing .env pattern |
| pyproject.toml | Configured | Uses uv_build backend, pytest.ini_options |
| GitHub Actions | None | No .github directory exists |
| pre-commit | None | No .pre-commit-config.yaml |
| coverage | None | pytest-cov not installed |
| .env.example | None | No secret documentation |

### Test Infrastructure

```
tests/
├── conftest.py          # Minimal: only marker registration
├── api/                 # API tests (task, dao_list_client)
├── bin/                 # CLI validation tests
├── db/                  # Database tests (jdb, rdb)
├── m/                   # Math tests
├── net/                 # Network tests (publisher, subscriber)
├── rs/                  # Serialization tests
├── sys/                 # File system tests
├── text/                # Text utility tests
├── time/                # Time/date tests
└── util/                # Utility tests
```

**Known issue:** `tests/db/test_misc.py::test_counter` - Pre-existing bug with JdbCounter

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| pytest-cov | 6.x | Coverage reporting with pytest integration | Industry standard, works with fail_under |
| coverage[toml] | 7.x | Coverage.py with pyproject.toml support | Required for coverage config in pyproject.toml |
| ruff | 0.9.x | Linting and formatting | Replaces black/isort/flake8, 10-100x faster |
| pre-commit | 4.x | Git hook management | Industry standard, large ecosystem |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| python-dotenv | 1.x | Load .env files | Optional - for local development |

### Already in Use (Do Not Replace)

| Library | Purpose |
|---------|---------|
| loguru | Logging - already used in 5 files |
| pytest | Testing framework |

### Installation

```bash
# Add to dev dependencies
uv add --dev pytest-cov coverage[toml] ruff pre-commit python-dotenv
```

## Architecture Patterns

### Recommended pyproject.toml Additions

```toml
# Coverage configuration
[tool.coverage.run]
source = ["jcx"]
branch = true
omit = [
    "*/tests/*",
    "*/__pycache__/*",
]

[tool.coverage.report]
fail_under = 80
show_missing = true
skip_covered = true
exclude_lines = [
    "pragma: no cover",
    "if TYPE_CHECKING:",
    "raise NotImplementedError",
    "@abstractmethod",
]

# Ruff configuration (extend existing ruff.toml)
[tool.ruff]
target-version = "py312"
line-length = 88

[tool.ruff.lint]
select = ["E4", "E7", "E9", "F", "I", "UP", "B"]
ignore = ["F403", "F405", "COM812"]

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
```

### Pattern 1: GitHub Actions Workflow with uv

**What:** CI/CD pipeline using uv for dependency management
**When to use:** This project uses uv as build backend

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  lint-and-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install uv
        uses: astral-sh/setup-uv@v5
        with:
          enable-cache: true

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install dependencies
        run: uv sync --dev

      - name: Lint with ruff
        run: uv run ruff check

      - name: Format check with ruff
        run: uv run ruff format --check

      - name: Run tests with coverage
        run: uv run pytest --cov=jcx --cov-fail-under=80

      - name: Upload coverage report
        uses: actions/upload-artifact@v4
        with:
          name: coverage-report
          path: htmlcov/
```

**Source:** [Astral uv GitHub](https://github.com/astral-sh/uv), [setup-python-uv-action](https://github.com/drivendataorg/setup-python-uv-action)

### Pattern 2: Pre-commit Configuration

**What:** Fast quality gates before commits land
**When to use:** All Python projects

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.9.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: local
    hooks:
      - id: pytest-cov
        name: pytest with coverage
        entry: uv run pytest --cov=jcx --cov-fail-under=80 -x
        language: system
        pass_filenames: false
        always_run: true
```

**Source:** [Ruff pre-commit integration](https://docs.astral.sh/ruff/integrations/#pre-commit)

### Pattern 3: Loguru JSON Configuration

**What:** Structured logging configuration for production
**When to use:** When structured logs needed for log aggregation

```python
# src/jcx/util/logging_config.py
import sys
import json
from loguru import logger

def configure_logging(json_format: bool = False, level: str = "INFO"):
    """Configure loguru for structured logging."""
    logger.remove()  # Remove default handler

    if json_format:
        def json_sink(message):
            record = message.record
            log_entry = {
                "timestamp": record["time"].isoformat(),
                "level": record["level"].name,
                "message": record["message"],
                "module": record["module"],
                "function": record["function"],
                "line": record["line"],
            }
            if record["extra"]:
                log_entry["extra"] = record["extra"]
            if record["exception"]:
                log_entry["exception"] = str(record["exception"])
            print(json.dumps(log_entry), file=sys.stderr)

        logger.add(json_sink, level=level)
    else:
        logger.add(
            sys.stderr,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            level=level,
        )
```

**Source:** [Loguru documentation](https://loguru.readthedocs.io/)

### Pattern 4: .env.example Template

**What:** Document required environment variables
**When to use:** Projects with configuration via environment

```bash
# .env.example
# Copy to .env and fill in values

# Database (optional)
DATABASE_URL=postgresql://user:password@localhost:5432/dbname

# Redis (optional)
REDIS_URL=redis://localhost:6379/0

# MQTT (optional)
MQTT_URL=tcp://localhost:1883

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json  # or 'text' for development
```

### Anti-Patterns to Avoid

- **Running full test suite in pre-commit**: Use `-x` flag to stop on first failure, or run quick unit tests only
- **Forgetting .env in .gitignore**: Always add `.env` to gitignore when adding .env.example
- **Configuring coverage without toml extra**: Must install `coverage[toml]` for pyproject.toml support
- **Using multiple linters**: Ruff replaces black, isort, flake8, pyupgrade, autoflake - use only ruff

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Coverage threshold enforcement | Custom script checking coverage output | `coverage[report].fail_under` | Built-in, reliable, exit codes |
| JSON logging | Custom log formatter | loguru with json sink | Already have loguru, just configure it |
| Import sorting | Manual import organization | ruff lint rule `I` | Automatic, consistent, fast |
| Test discovery | Custom test runner | pytest with markers | Industry standard, rich ecosystem |

**Key insight:** The project already uses loguru. Do not add structlog - configure loguru for structured output instead.

## Common Pitfalls

### Pitfall 1: Coverage Not Failing on Threshold

**What goes wrong:** pytest-cov runs but exits 0 even when coverage is below threshold
**Why it happens:** Missing `coverage[toml]` package or wrong config location
**How to avoid:**
1. Install `coverage[toml]` (not just `coverage`)
2. Put config in `[tool.coverage.report]` in pyproject.toml
3. Use `--cov-fail-under=80` CLI flag as backup
**Warning signs:** Coverage report shows <80% but CI passes

### Pitfall 2: Pre-commit Too Slow

**What goes wrong:** Developers skip pre-commit because it takes too long
**Why it happens:** Running all tests on every commit
**How to avoid:**
1. Run only linting/formatting on pre-commit
2. Run coverage check only on push or in CI
3. Use `uv run` for faster startup
**Warning signs:** Commits with `--no-verify` becoming common

### Pitfall 3: Ruff Conflicts with Existing Tools

**What goes wrong:** Ruff format conflicts with black, or lint with flake8
**Why it happens:** Multiple tools trying to do the same thing
**How to avoid:**
1. Remove black, isort, flake8, pyupgrade from dependencies
2. Use only ruff for linting AND formatting
3. Configure ruff to match existing style
**Warning signs:** CI fails with formatting conflicts

### Pitfall 4: .env File Committed

**What goes wrong:** Secrets exposed in git history
**Why it happens:** Forgetting to add .env to .gitignore
**How to avoid:**
1. Add `.env` to .gitignore BEFORE creating .env.example
2. Use `git secrets` or similar scanner
3. Document in CONTRIBUTING.md
**Warning signs:** `.env` not in .gitignore, or git status shows .env

## Code Examples

### pytest-cov Configuration

```toml
# pyproject.toml
[tool.pytest.ini_options]
addopts = "-m 'not integration' --cov=jcx --cov-report=term-missing --cov-report=html"
markers = [
    "integration: marks tests as integration tests (deselect with '-m \"not integration\"')",
]

[tool.coverage.run]
source = ["jcx"]
branch = true

[tool.coverage.report]
fail_under = 80
show_missing = true
exclude_lines = [
    "pragma: no cover",
    "if TYPE_CHECKING:",
]
```

**Source:** [pytest-cov documentation](https://pytest-cov.readthedocs.io/en/latest/config.html)

### Running Coverage

```bash
# Quick check (fails if < 80%)
uv run pytest --cov=jcx --cov-fail-under=80

# Full report with HTML
uv run pytest --cov=jcx --cov-report=html --cov-report=term-missing

# Run only unit tests (exclude integration)
uv run pytest -m "not integration" --cov=jcx
```

### Ruff Configuration Migration

```toml
# ruff.toml - Extended from current minimal config
target-version = "py312"
line-length = 88

[lint]
# Enable: pycodestyle errors, Pyflakes, isort, pyupgrade, bugbear
select = ["E4", "E7", "E9", "F", "I", "UP", "B"]
ignore = ["F403", "F405", "COM812"]

[lint.per-file-ignores]
"tests/*" = ["S101"]  # Allow assert in tests

[format]
quote-style = "double"
indent-style = "space"
skip-magic-trailing-comma = false
```

**Source:** [Ruff configuration docs](https://docs.astral.sh/ruff/configuration/)

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| black + isort + flake8 | ruff alone | 2023-2024 | 10-100x faster, one tool |
| pip + requirements.txt | uv + pyproject.toml | 2024-2025 | Faster installs, better lockfile |
| coverage.py CLI flags | pyproject.toml config | 2020+ | Centralized config |
| Custom logging config | loguru/structlog | 2020+ | Simpler API, structured output |

**Deprecated/outdated:**
- **black/isort/flake8**: Replaced by ruff
- **pip-tools**: Replaced by uv
- **setup.py**: Replaced by pyproject.toml

## Open Questions

1. **Should pre-commit run full coverage check?**
   - What we know: Full test suite can be slow (26 test files)
   - What's unclear: Actual test execution time
   - Recommendation: Run linting only in pre-commit, coverage in CI. Add optional hook for coverage.

2. **Integration tests in CI?**
   - What we know: `@pytest.mark.integration` exists, tests excluded by default
   - What's unclear: Do integration tests require external services (Redis, MQTT)?
   - Recommendation: Keep integration tests excluded from CI until services are mocked or test containers added.

3. **Coverage threshold: 80% realistic?**
   - What we know: 84 source files, 26 test files (31% test-to-source ratio)
   - What's unclear: Current coverage percentage
   - Recommendation: Run baseline coverage first. If < 80%, set lower threshold and increment.

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest 9.0.1 |
| Config file | pyproject.toml [tool.pytest.ini_options] |
| Quick run command | `uv run pytest -m "not integration" -x` |
| Full suite command | `uv run pytest --cov=jcx --cov-fail-under=80` |

### Phase Requirements -> Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| QLTY-01 | Coverage reports with 80% threshold | config | `uv run pytest --cov=jcx --cov-fail-under=80` | Wave 0 |
| QLTY-02 | CI/CD pipeline runs on push/PR | workflow | `gh workflow run ci.yml` (after merge) | Wave 0 |
| QLTY-03 | Ruff lints and formats code | config | `uv run ruff check && uv run ruff format --check` | Wave 0 |
| QLTY-04 | Pre-commit hooks enforce quality | config | `pre-commit run --all-files` | Wave 0 |
| QLTY-05 | Structured logging available | unit | `uv run pytest tests/util/logging_test.py` | Wave 0 |
| SEC-05 | .env.example documents secrets | manual | N/A - documentation task | Wave 0 |

### Sampling Rate

- **Per task commit:** `uv run pytest -m "not integration" -x`
- **Per wave merge:** `uv run pytest --cov=jcx`
- **Phase gate:** `uv run pytest --cov=jcx --cov-fail-under=80` must pass

### Wave 0 Gaps

- [ ] `tests/util/logging_config_test.py` - Test structured logging configuration
- [ ] `.github/workflows/ci.yml` - GitHub Actions workflow
- [ ] `.pre-commit-config.yaml` - Pre-commit hooks
- [ ] `.env.example` - Secret documentation
- [ ] `pyproject.toml` - Add coverage and ruff config
- [ ] `.gitignore` - Add `.env` pattern

## Dependencies Between Plans

```
QLTY-03 (Ruff config) ──────────────────┐
                                        │
QLTY-01 (Coverage config) ──────────────┼──> QLTY-02 (CI/CD)
                                        │
QLTY-04 (Pre-commit) ───────────────────┘
        │
        └──> Requires QLTY-03 for ruff hooks

QLTY-05 (Logging) ──────> Independent

SEC-05 (Secret docs) ───> Independent
```

**Recommended execution order:**
1. QLTY-03: Configure ruff (extends existing ruff.toml)
2. QLTY-01: Add pytest-cov configuration
3. QLTY-02: Create GitHub Actions workflow (depends on 1, 2)
4. QLTY-04: Add pre-commit hooks (depends on 1)
5. QLTY-05: Add structured logging config (independent)
6. SEC-05: Document secrets in .env.example (independent)

## Sources

### Primary (HIGH confidence)

- [Ruff Configuration Documentation](https://docs.astral.sh/ruff/configuration/) - Official Astral docs
- [pytest-cov Configuration](https://pytest-cov.readthedocs.io/en/latest/config.html) - Official docs
- [Astral uv GitHub](https://github.com/astral-sh/uv) - Official repository
- [coverage.py Documentation](https://coverage.readthedocs.io/) - Official docs

### Secondary (MEDIUM confidence)

- [Better Stack: Python Logging Libraries Comparison](https://betterstack.com/community/guides/logging/best-python-logging-libraries/) - Comprehensive comparison of loguru vs structlog
- [GitHub Actions: Building and testing Python](https://docs.github.com/en/actions/tutorials/build-and-test-code/python) - Official GitHub docs
- [Real Python: Managing Projects with uv](https://realpython.com/python-uv/) - Comprehensive guide

### Tertiary (LOW confidence)

- [Medium: CI/CD for Python with GitHub Actions](https://medium.com/algomart/ci-cd-for-python-projects-using-github-actions-4a2055ed2c05) - General guidance

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - All tools are mature, well-documented, and widely adopted
- Architecture: HIGH - Patterns are standard for modern Python projects
- Pitfalls: HIGH - Based on official documentation and common issues

**Research date:** 2026-03-22
**Valid until:** 2026-06-22 (3 months - stable tooling)

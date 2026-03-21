# Stack Research

**Domain:** Python utility library refactoring for quality improvement
**Researched:** 2026-03-21
**Confidence:** HIGH

## Recommended Stack

### Core Technologies

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| Ruff | 0.14.3+ | All-in-one linter & formatter | Replaces black, isort, flake8, pyupgrade, pydocstyle, autoflake, and 20+ tools. Written in Rust, 10-100x faster. Actively maintained by Astral (uv creators). Single config in `pyproject.toml`. |
| pytest | 8.0+ | Test framework | Industry standard for Python testing. Rich plugin ecosystem. Already in use - keep and enhance. |
| pytest-cov | 7.0.0+ | Coverage reporting | Required for measuring test effectiveness. Currently missing in project. Integrates seamlessly with pytest. |
| Pyright | 1.1.390+ | Type checker | 3-5x faster than mypy. Better inference for modern Python patterns. Used by VS Code Pylance. Recommended for speed-focused CI/CD. |
| pre-commit | 4.0+ | Git hooks framework | Enforces quality gates before commits. Catches issues early. Industry standard for CI/CD quality. |

### Supporting Libraries

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| returns | 0.24.0+ | Functional error handling | Replace rustshed gradually. Better Python idioms, active maintenance, Pydantic integration. Use for new code, migrate existing when touching. |
| pydantic | 2.0+ | Data validation | Already in use. Keep and ensure all models use v2 patterns. |
| loguru | 0.7+ | Logging | Already in use. Add centralized configuration. |
| pytest-asyncio | 0.24+ | Async test support | If async patterns are added later (out of scope now, but preparation). |
| pytest-mock | 3.14+ | Mocking utilities | For cleaner test mocking patterns. Project has 64 mock references but pattern unclear. |

### Development Tools

| Tool | Purpose | Notes |
|------|---------|-------|
| uv | Package manager | Already in use. Faster than pip, modern lockfile. Keep. |
| pre-commit-hooks | Standard git hooks | Includes trailing-whitespace, end-of-file-fixer, check-yaml, check-json. |
| ruff-pre-commit | Ruff in pre-commit | Use `ruff --fix` in pre-commit for auto-formatting. |

## Installation

```bash
# Core quality tools (add to dev dependencies)
uv add --dev pytest-cov pyright pre-commit

# Supporting
uv add --dev returns pytest-mock

# pre-commit setup
pre-commit install
```

## Alternatives Considered

| Recommended | Alternative | When to Use Alternative |
|-------------|-------------|-------------------------|
| Pyright | Mypy | If you need plugin ecosystem (django-stubs, sqlalchemy-stubs). Mypy has mature plugin support. Slower but more extensible. |
| returns | rustshed | If codebase is deeply integrated with rustshed and migration cost is too high. returns is more Pythonic but requires migration effort. |
| Ruff | black + isort + flake8 | Legacy projects that can't change tooling. No reason for new/active projects. |

## What NOT to Use

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| flake8 | Superseded by Ruff. Slower, fragmented configuration. | Ruff (includes all flake8 rules) |
| black | Superseded by Ruff format. Separate tool to manage. | Ruff format (100% compatible with black) |
| isort | Superseded by Ruff isort. Separate tool to manage. | Ruff isort (built-in) |
| pyupgrade | Superseded by Ruff UP rules. | Ruff (includes pyupgrade rules) |
| pylint | Overlaps with Ruff. Different architecture. | Ruff (covers most pylint rules, faster) |
| assert statements | Disabled with `python -O`. Not for runtime validation. | Result/Option types, explicit validation |

## Stack Patterns by Variant

**For CI/CD pipeline:**
- Use Pyright for fast type checking (3-5x speed advantage)
- Run `ruff check --output-format=github` for PR annotations
- Coverage threshold: 80% minimum (project requirement)

**For IDE integration:**
- Pyright/Pylance for real-time type feedback
- Ruff for real-time linting and formatting

**For gradual rustshed migration:**
- New code: Use `returns` library
- Existing code: Keep rustshed until natural refactoring opportunity
- Coexistence possible: `from returns.result import Result` vs `from rustshed import Result`

## Version Compatibility

| Package | Compatible With | Notes |
|---------|-----------------|-------|
| Ruff 0.14+ | Python 3.8+ | Project uses 3.12 - fully compatible |
| pytest-cov 7.0+ | pytest 8.0+ | Requires pytest 7.4+ minimum |
| Pyright | Python 3.8+ | Excellent 3.12 support with new type features |
| returns 0.24+ | Python 3.10+ | Project uses 3.12 - fully compatible |

## Configuration Recommendations

### Ruff (`ruff.toml` or `pyproject.toml`)
```toml
[tool.ruff]
target-version = "py312"
select = ["ALL"]  # Already configured
ignore = [
    "D",      # Docstrings (add gradually)
    "ANN",    # Type annotations (add gradually)
    "COM",    # Trailing commas (formatter handles)
]

[tool.ruff.format]
quote-style = "double"
line-length = 100
```

### Pyright (`pyproject.toml`)
```toml
[tool.pyright]
pythonVersion = "3.12"
typeCheckingMode = "standard"
reportMissingTypeStubs = false
```

### pytest-cov (`pyproject.toml`)
```toml
[tool.pytest.ini_options]
addopts = "--cov=src/jcx --cov-report=term-missing --cov-fail-under=80"
testpaths = ["tests"]
```

### pre-commit (`.pre-commit-config.yaml`)
```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.14.3
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v5.0.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-json
```

## Sources

- PyPI Ruff: https://pypi.org/project/ruff/ — version 0.14.3 (HIGH confidence)
- PyPI pytest-cov: https://pypi.org/project/pytest-cov/ — version 7.0.0 (HIGH confidence)
- Astral (Ruff creators): https://astral.sh/ — official tool builder (HIGH confidence)
- dry-python/returns: https://github.com/dry-python/returns — active maintenance, 0.24.0 (HIGH confidence)
- Pyright vs Mypy benchmarks: community benchmarks show 3-5x speed advantage (MEDIUM confidence)
- pre-commit documentation: https://pre-commit.com/ — official docs (HIGH confidence)

---
*Stack research for: Python library quality refactoring*
*Researched: 2026-03-21*

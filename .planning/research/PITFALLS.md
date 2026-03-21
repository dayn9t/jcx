# Pitfalls Research

**Domain:** Python library refactoring (Rust-style patterns, Pydantic, error handling)
**Researched:** 2026-03-21
**Confidence:** HIGH (official documentation + multiple community sources + project context)

## Critical Pitfalls

### Pitfall 1: Pydantic V1 to V2 Migration Without Test Updates

**What goes wrong:**
Tests break silently after Pydantic migration. Validation errors change structure, methods are renamed (`dict()` → `model_dump()`), and field behavior changes (Optional fields now required by default). Tests pass in isolation but fail in integration.

**Why it happens:**
Pydantic V2 is a ground-up rewrite with a Rust core. The API surface changed dramatically:
- Method renames: `.dict()` → `.model_dump()`, `.parse_obj()` → `.model_validate()`
- `@validator` → `@field_validator` with different signatures
- `Optional[T]` fields are now REQUIRED unless given `= None` default
- ValidationError structure changed

**How to avoid:**
1. Run `bump-pydantic` tool first for automated migration
2. Update all test assertions that check ValidationError structure
3. Search for every `.dict()`, `.json()`, `.parse_obj()` call and update
4. Review all `Optional[T]` annotations - add `= None` if field should be optional
5. Run full test suite after migration, fix ALL failures before committing

**Warning signs:**
- Tests importing from `pydantic` instead of `pydantic.v1` during transition
- `DeprecationWarning` in test output
- ValidationError assertions checking old error format
- Fields marked Optional but no `= None` default

**Phase to address:** Phase 1 (Test Repair) - MUST be resolved before any other refactoring

---

### Pitfall 2: `unwrap()` Panics in Production

**What goes wrong:**
Rust-style `Option.unwrap()` or `Result.unwrap()` calls crash the application at runtime when encountering None/Err values. In jcx: 33 `.unwrap()` calls throughout the codebase that can panic.

**Why it happens:**
Developers adopt Rust-style Option/Result types but use `.unwrap()` as a quick way to extract values during development. Unlike Rust's compile-time guarantees, Python's version has no safety net - unwrap panics at runtime.

**How to avoid:**
Replace all `.unwrap()` with safe alternatives:
```python
# BAD - panics on None
value = option.unwrap()

# GOOD - provides default
value = option.unwrap_or(default_value)
value = option.unwrap_or_else(lambda: compute_default())

# GOOD - explicit error handling
match option:
    case Some(v):
        return v
    case None:
        raise ValueError("Expected value")
```

**Warning signs:**
- grep for `.unwrap()` returns results
- Code reviews showing `.unwrap()` without explicit None handling
- Tests that don't cover None/Err paths
- Error messages mentioning "called unwrap on None"

**Phase to address:** Phase 2 (Error Handling) - Replace all unwrap calls with safe patterns

---

### Pitfall 3: Assert Statements in Production Code

**What goes wrong:**
Critical validation checks using `assert` statements are silently skipped when Python runs in optimized mode (`-O` or `-OO` flags). Security checks, data validation, and invariant enforcement disappear in production.

**Why it happens:**
Developers use `assert` for quick validation during development, not realizing:
1. `assert` is for debugging invariants, not runtime validation
2. Production deployments often use `-O` flag for performance
3. `assert condition, "message"` becomes a no-op when optimized

**How to avoid:**
Replace ALL assert statements with proper validation:
```python
# BAD - removed in optimized mode
assert url is not None, "URL required"
assert value > 0, "Value must be positive"

# GOOD - always runs
if url is None:
    raise ValueError("URL required")
if value <= 0:
    raise ValueError("Value must be positive")

# Or use Result/Option types
def validate_url(url: str | None) -> Result[str, ValueError]:
    if url is None:
        return Err(ValueError("URL required"))
    return Ok(url)
```

**Warning signs:**
- `assert` statements in `src/` (not `tests/`)
- Security checks using `assert`
- Data validation using `assert`
- Invariant checks that must run in production

**Phase to address:** Phase 2 (Error Handling) - Replace all production asserts

---

### Pitfall 4: Broad Exception Handling Hiding Errors

**What goes wrong:**
`except Exception as e:` clauses catch and silently handle critical errors like MemoryError, KeyboardInterrupt, or unexpected bugs. Debugging becomes impossible because error context is lost.

**Why it happens:**
Developers use broad exception handling to "make code robust" but actually make it fragile:
- Hides bugs that should surface
- Loses stack traces and error context
- Makes debugging production issues nearly impossible
- Can catch system-level exceptions that should propagate

**How to avoid:**
1. Catch SPECIFIC exceptions only:
```python
# BAD
try:
    result = api_call()
except Exception as e:
    logger.error(e)

# GOOD
try:
    result = api_call()
except requests.Timeout:
    logger.warning("API timeout, retrying...")
    return retry()
except requests.ConnectionError as e:
    logger.error(f"Connection failed: {e}")
    raise ServiceUnavailableError() from e
```

2. If you must catch Exception, re-raise after logging:
```python
try:
    risky_operation()
except Exception as e:
    logger.exception("Unexpected error")
    raise  # Re-raise to not hide it
```

3. Never use bare `except:` - it catches KeyboardInterrupt and SystemExit

**Warning signs:**
- `except Exception:` without re-raise
- `except:` (bare except)
- `except Exception as e: pass` or empty handler body
- Multiple exception types in single except clause without differentiation

**Phase to address:** Phase 2 (Error Handling) - Audit and fix all broad exception handlers

---

### Pitfall 5: Breaking Tests During Refactoring

**What goes wrong:**
Refactoring changes implementation but tests aren't updated. Tests either:
1. Pass when they shouldn't (testing old behavior)
2. Fail when they shouldn't (brittle tests tied to implementation)
3. Hang or timeout (like MQTT subscriber test in jcx)

**Why it happens:**
Tests written against implementation details rather than contracts. When refactoring:
- Private method tests break on signature changes
- Integration tests depend on specific error messages
- Mock setups don't match new implementation
- Async/blocking mismatches cause hangs

**How to avoid:**
1. **Test public APIs, not implementation** - Tests should survive refactoring if contract unchanged
2. **Fix ALL failing tests before committing** - Never commit with skipped/broken tests
3. **Use TDD for refactoring** - Write characterization tests first
4. **Run full test suite frequently** - After each significant change
5. **Update tests as part of refactoring** - Not as separate task

For jcx specifically:
- Fix MQTT subscriber test hang (use async test patterns or proper mocking)
- Repair all Pydantic-related test failures
- Add integration tests for fragile areas before touching them

**Warning signs:**
- `@pytest.mark.skip` or `# FIXME` in tests
- Tests commented out
- CI shows failing tests ignored
- Tests only pass with specific mock setups

**Phase to address:** Phase 1 (Test Repair) - Fix all broken tests before any other work

---

### Pitfall 6: Type Ignore Comments Masking Real Errors

**What goes wrong:**
`# type: ignore` comments suppress type checker warnings, hiding genuine type errors that cause runtime failures. In jcx: 9 `# type: ignore` comments potentially hiding bugs.

**Why it happens:**
When type checking is added to existing code:
- Some type errors are hard to fix immediately
- Developers add `# type: ignore` as "temporary" workaround
- Temporary becomes permanent, hiding future type regressions
- Type checker can't warn about new type errors in ignored lines

**How to avoid:**
1. **Never add type: ignore without a TODO comment explaining why**
2. **Fix the type error instead of ignoring when possible**
3. **Review all existing type: ignore comments** - are they still needed?
4. **Use more specific ignore** (e.g., `# type: ignore[arg-type]`)
5. **Add type stubs for external libraries** instead of ignoring

**Warning signs:**
- `# type: ignore` without explanation
- Type: ignore on lines that changed recently
- Runtime errors in areas with type: ignore
- Type checker disabled for entire files

**Phase to address:** Phase 3 (Type Safety) - Review and fix or document all type: ignore comments

---

### Pitfall 7: "Fancy" Refactoring Making Code Worse

**What goes wrong:**
Developers apply patterns they learned without considering context. Code becomes harder to read, slower, or more complex for no benefit.

Example from research:
```python
# Original - clear and simple
if (self.temperature > MAX_TEMPERATURE
    or self.pressure > MAX_PRESSURE):
    ...

# "Refactored" - more complex, slower
if any([self.temperature > MAX_TEMPERATURE,
        self.pressure > MAX_PRESSURE]):
    ...
```

**Why it happens:**
- Desire to use new patterns/techniques
- Misunderstanding when patterns are appropriate
- Refactoring without clear goal
- "Clever" code prioritized over readable code

**How to avoid:**
1. **Refactor with a purpose** - What specific problem are you solving?
2. **Measure before and after** - Is code actually better?
3. **Prefer simple over clever** - Readability > cleverness
4. **Apply patterns where they fit** - Not everywhere
5. **Get code review** - Fresh eyes spot over-engineering

**Warning signs:**
- Refactoring PRs without clear problem statement
- Increased line count without added functionality
- More complex logic for same outcome
- Performance regression in benchmarks

**Phase to address:** Every phase - Constant vigilance in code review

---

## Technical Debt Patterns

Shortcuts that seem reasonable but create long-term problems.

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| `# type: ignore` | Type errors go away | Hides real bugs, prevents type safety | Never without documented TODO |
| `except Exception:` | Handles all errors | Hides bugs, loses context | Never - use specific exceptions |
| `.unwrap()` | Quick value extraction | Runtime panics | Only in tests with guaranteed values |
| `assert` for validation | Quick checks | Skipped in production (-O flag) | Never - use proper validation |
| Skip broken test | CI passes | Bugs undetected | Never - fix the test |
| Commented code | "Save for later" | Confusion, rot | Never - delete it (git remembers) |

## Integration Gotchas

Common mistakes when connecting to external services.

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| HTTP Client (requests) | No timeout, no connection limits | Set timeout, configure HTTPAdapter pool limits |
| Redis | URL parsing with assert | Use Result type, validate before parsing |
| MQTT | Test hangs on message loop | Use async test patterns or mock message loop |
| Flask-RESTX | Manual model generation | Consider FastAPI with auto Pydantic model generation |
| Pydantic | V1 patterns in V2 codebase | Use V2 patterns exclusively or migrate fully |

## Performance Traps

Patterns that work at small scale but fail as usage grows.

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|----------------|
| Multiple `unwrap()` calls | Runtime panics on edge cases | Use `unwrap_or()`, `unwrap_or_else()` | First None value encountered |
| File-based database (jdb) | Slow with thousands of records | Paginate, migrate to SQLite for scale | ~1000+ records |
| Blocking I/O | Can't handle concurrent requests | Use async/await (future consideration) | Multiple concurrent users |
| No connection pooling | Connection exhaustion | Configure HTTPAdapter with pool limits | High request volume |
| Global mutable state | Race conditions, data corruption | Use thread-local storage or locks | Multiple threads |

## Security Mistakes

Domain-specific security issues beyond general web security.

| Mistake | Risk | Prevention |
|---------|------|------------|
| Assert for URL validation | Validation skipped in production | Use proper if/raise validation |
| No input validation in CLI | Injection, path traversal | Validate all inputs before operations |
| Broad exception handling | Security errors hidden | Catch specific exceptions, log security events |
| No secret management | Credentials in code | Use environment variables, .env files |
| HTTP without timeout | DoS vulnerability | Always set timeout on HTTP requests |

## "Looks Done But Isn't" Checklist

Things that appear complete but are missing critical pieces.

- [ ] **Pydantic Migration:** Often missing test updates — verify ALL tests pass
- [ ] **Error Handling:** Often missing specific exception types — grep for `except Exception`
- [ ] **Type Safety:** Often missing type: ignore cleanup — grep for `# type: ignore`
- [ ] **Assert Removal:** Often missing production assert statements — grep for `assert` in `src/`
- [ ] **Unwrap Replacement:** Often missing edge case handling — grep for `.unwrap()`
- [ ] **Test Coverage:** Often missing integration tests — verify coverage includes fragile areas
- [ ] **API Compatibility:** Often missing breaking change documentation — check API signatures changed

## Recovery Strategies

When pitfalls occur despite prevention, how to recover.

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| Pydantic migration test failures | MEDIUM | 1. Run bump-pydantic tool 2. Update test assertions 3. Fix Optional fields 4. Run full suite |
| Unwrap panics in production | HIGH | 1. Identify crash location 2. Add proper error handling 3. Add tests for None path 4. Deploy fix |
| Assert validation bypassed | HIGH | 1. Audit all assert usage 2. Replace with if/raise 3. Add tests 4. Verify in production |
| Broad exception hiding bugs | MEDIUM | 1. Identify catch blocks 2. Make exceptions specific 3. Add logging 4. Re-raise when appropriate |
| Tests broken by refactoring | MEDIUM | 1. Revert if possible 2. Update tests to match new contracts 3. Run full suite 4. Fix all failures |
| Type ignores hiding errors | LOW | 1. Review each type: ignore 2. Fix underlying issue 3. Remove ignore or document why needed |

## Pitfall-to-Phase Mapping

How roadmap phases should address these pitfalls.

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| Pydantic migration test failures | Phase 1 (Test Repair) | All tests pass, no deprecation warnings |
| Unwrap panics | Phase 2 (Error Handling) | grep for `.unwrap()` returns 0 results in src/ |
| Assert in production | Phase 2 (Error Handling) | grep for `^\s*assert` in src/ returns 0 results |
| Broad exception handling | Phase 2 (Error Handling) | No `except Exception:` without re-raise |
| Tests broken by refactoring | Phase 1 (Test Repair) | 100% of tests pass, no skipped tests |
| Type ignore comments | Phase 3 (Type Safety) | All type: ignore have TODO comments or are fixed |
| Fancy refactoring | Every phase (code review) | Code review checklist includes simplicity check |

## Sources

- [Pydantic Migration Guide](https://docs.pydantic.dev/latest/migration/) - Official documentation (HIGH confidence)
- [Avoiding Exception Handling Anti-patterns in Python](https://medium.com/@jefmoura/avoiding-the-pitfalls-common-anti-patterns-in-exception-handling-in-python-12139e05b6) - Medium (MEDIUM confidence)
- [A Python Refactoring Gone Wrong](https://dbader.org/blog/python-refactoring-gone-wrong) - dbader.org (HIGH confidence)
- [Python Assert Best Practices](https://stackoverflow.com/questions/944592/best-practice-for-using-assert) - Stack Overflow (HIGH confidence)
- [Rust Option/Result Documentation](https://doc.rust-lang.org/rust-by-example/error/option_unwrap.html) - Official Rust docs (HIGH confidence)
- [Python Type Hinting Challenges](https://www.reddit.com/r/Python/comments/10zdidm/why_type_hinting_sucks/) - Reddit discussion (MEDIUM confidence)
- [Test-Driven Refactoring](https://www.thedigitalcatonline.com/blog/2017/07/21/refactoring-with-test-in-python-a-practical-example/) - The Digital Cat (HIGH confidence)
- [Flask to FastAPI Migration](https://www.reddit.com/r/Python/comments/10h9fb5/migrating_from_flask_to_fastapi/) - Reddit (MEDIUM confidence)
- Project CONCERNS.md analysis - Internal codebase analysis (HIGH confidence)

---
*Pitfalls research for: Python library refactoring with Rust-style patterns and Pydantic*
*Researched: 2026-03-21*
